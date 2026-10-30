import subprocess
import sys


EXPECTED = "magnusbakken@gmail.com"


def fail(message):
    print(f"Identity check failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def git(*arguments):
    result = subprocess.run(
        ["git", *arguments], text=True, capture_output=True,
    )
    if result.returncode:
        fail(f"cannot inspect Git metadata: {result.stderr.strip()}")
    return result.stdout.strip()


def check(author, committer, label):
    if author != EXPECTED or committer != EXPECTED:
        fail(f"{label} requires personal author and committer {EXPECTED}; "
             f"found {author} / {committer}")


def identity_email(variable):
    identity = git("var", variable)
    prefix, separator, suffix = identity.rpartition("<")
    email, closing, remainder = suffix.partition(">")
    if not prefix or not separator or not closing or not remainder:
        fail(f"cannot parse {variable}")
    return email


def main():
    if sys.argv[1:] == ["commit"]:
        check(identity_email("GIT_AUTHOR_IDENT"),
              identity_email("GIT_COMMITTER_IDENT"), "new commit")
    elif sys.argv[1:] == ["push"]:
        for line in sys.stdin:
            fields = line.split()
            if len(fields) != 4:
                fail("invalid pre-push input")
            local_ref, local_oid, remote_ref, remote_oid = fields
            if local_ref == "(delete)":
                continue
            new = git("rev-parse", "--verify", f"{local_oid}^{{commit}}")
            if set(remote_oid) == {"0"}:
                revision = new
            else:
                old = git("rev-parse", "--verify", f"{remote_oid}^{{commit}}")
                revision = f"{old}..{new}"
            records = git("log", "--format=%H%x00%ae%x00%ce", revision)
            for record in records.splitlines():
                commit, author, committer = record.split("\x00")
                check(author, committer, f"{remote_ref}: {commit}")
    else:
        fail("usage: identity-check.py commit|push")


if __name__ == "__main__":
    main()
