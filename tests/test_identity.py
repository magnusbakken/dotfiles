import os
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
PERSONAL = "magnusbakken@gmail.com"
OTHER = "other@example.invalid"


class IdentityTest(unittest.TestCase):
    def setUp(self):
        self.root = ROOT / ".worktrees" / "identity-tests" / self._testMethodName
        self.root.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.root)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.env = {
            "HOME": str(self.root),
            "PATH": os.environ["PATH"],
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
        }
        self.git("init", "--initial-branch=main")
        self.git("config", "user.name", "Fixture User")
        self.git("config", "user.email", PERSONAL)
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.hooksPath", ".githooks")
        shutil.copytree(ROOT / ".githooks", self.repo / ".githooks")
        self.git("commit", "--allow-empty", "-m", "personal root")

    def git(self, *args, extra_env=None, ok=True):
        environment = dict(self.env)
        environment.update(extra_env or {})
        result = subprocess.run(
            ["git", *args], cwd=self.repo, env=environment,
            text=True, capture_output=True,
        )
        if ok:
            self.assertEqual(result.returncode, 0,
                             result.stdout + result.stderr)
        return result

    def test_personal_commit_succeeds(self):
        self.git("commit", "--allow-empty", "-m", "personal")
        result = self.git("show", "-s", "--format=%ae %ce")
        self.assertEqual(result.stdout.strip(), f"{PERSONAL} {PERSONAL}")

    def test_other_identities_cannot_create_a_normal_commit(self):
        original = self.git("rev-parse", "HEAD").stdout
        cases = (
            (("--author", f"Other <{OTHER}>"), {}),
            ((), {"GIT_AUTHOR_EMAIL": OTHER}),
            ((), {"GIT_COMMITTER_EMAIL": OTHER}),
        )
        for arguments, environment in cases:
            with self.subTest(arguments=arguments, environment=environment):
                result = self.git(
                    "commit", "--allow-empty", "-m", "reject",
                    *arguments, extra_env=environment, ok=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("identity", result.stderr.lower())
                self.assertEqual(
                    self.git("rev-parse", "HEAD").stdout, original
                )

    def assert_bad_ancestor_cannot_be_pushed(self, seed_remote):
        remote = self.root / "remote.git"
        self.git("init", "--bare", "--initial-branch=main", str(remote))
        self.git("remote", "add", "origin", str(remote))
        if seed_remote:
            self.git("push", "origin", "main")
        self.git(
            "-c", "core.hooksPath=/dev/null", "-c", f"user.email={OTHER}",
            "commit", "--allow-empty", "-m", "deliberately bypassed hook",
        )
        self.git("commit", "--allow-empty", "-m", "personal tip")
        before = self.git("ls-remote", "origin").stdout
        result = self.git("push", "origin", "main", ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("identity", result.stderr.lower())
        self.assertEqual(self.git("ls-remote", "origin").stdout, before)

    def test_push_checks_ancestors_on_an_existing_remote_branch(self):
        self.assert_bad_ancestor_cannot_be_pushed(True)

    def test_push_checks_full_history_for_a_new_remote_branch(self):
        self.assert_bad_ancestor_cannot_be_pushed(False)

    def test_personal_history_can_be_pushed(self):
        remote = self.root / "remote.git"
        self.git("init", "--bare", "--initial-branch=main", str(remote))
        self.git("remote", "add", "origin", str(remote))
        self.git("push", "origin", "main")
        expected = self.git("rev-parse", "HEAD").stdout.strip()
        actual = self.git("ls-remote", "origin", "refs/heads/main").stdout
        self.assertEqual(actual.split()[0], expected)
