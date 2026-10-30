import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = (
    "shell", "zsh", "git", "tmux", "kitty", "fzf",
    "desktop", "tmux-service",
)


class PackagesTest(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(shutil.which("stow"), "GNU Stow is required")
        temporary = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.home = self.root / "home"
        self.checkout = self.root / "checkout"
        self.home.mkdir()
        self.checkout.mkdir()
        self.env = {
            "HOME": str(self.home),
            "PATH": os.environ["PATH"],
            "GIT_CONFIG_GLOBAL": str(self.home / ".gitconfig"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CEILING_DIRECTORIES": str(self.root),
        }
        self.expected = {}
        for package in PACKAGES:
            shutil.copytree(ROOT / package, self.checkout / package)
            for path in (self.checkout / package).rglob("*"):
                if path.is_file():
                    relative = path.relative_to(self.checkout / package)
                    self.expected[relative] = path

    def run_command(self, command, ok=True):
        result = subprocess.run(
            command, cwd=self.checkout, env=self.env,
            text=True, capture_output=True,
        )
        if ok:
            self.assertEqual(result.returncode, 0,
                             result.stdout + result.stderr)
        return result

    def stow(self, *arguments, ok=True):
        return self.run_command(
            ["stow", "--dir", str(self.checkout),
             "--target", str(self.home), "--no-folding",
             *arguments, *PACKAGES], ok=ok,
        )

    def test_preview_install_repeat_and_unstow(self):
        self.stow("--simulate", "--verbose")
        self.assertEqual(list(self.home.iterdir()), [])
        before = {relative: path.read_bytes()
                  for relative, path in self.expected.items()}
        self.stow()
        observed = {
            path.relative_to(self.home)
            for path in self.home.rglob("*") if path.is_symlink()
        }
        self.assertEqual(observed, set(self.expected))
        for relative, source in self.expected.items():
            destination = self.home / relative
            self.assertEqual(destination.resolve(), source)
            for parent in destination.parents:
                if parent == self.home:
                    break
                self.assertFalse(parent.is_symlink(), str(parent))
        self.stow()
        self.stow("--delete")
        for relative, source in self.expected.items():
            self.assertFalse(os.path.lexists(self.home / relative))
            self.assertEqual(source.read_bytes(), before[relative])

    def test_foreign_link_conflict_does_not_change_other_destinations(self):
        foreign = self.root / "other-checkout"
        foreign.write_text("unmanaged\n")
        destination = self.home / ".zshrc"
        destination.symlink_to(foreign)
        result = self.stow(ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(".zshrc", result.stderr)
        self.assertEqual(list(self.home.iterdir()), [destination])
        self.assertEqual(destination.resolve(), foreign)

    def test_plain_file_conflict_including_identical_contents(self):
        destination = self.home / ".zshrc"
        for contents in (b"unmanaged\n",
                         (self.checkout / "zsh/.zshrc").read_bytes()):
            with self.subTest(contents_identical=contents != b"unmanaged\n"):
                destination.write_bytes(contents)
                result = self.stow(ok=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(destination.read_bytes(), contents)
                self.assertEqual(list(self.home.iterdir()), [destination])
                destination.unlink()

    def test_portable_environment_and_synthetic_local_override(self):
        (self.home / "bin").mkdir()
        (self.home / ".local/bin").mkdir(parents=True)
        profile = self.checkout / "shell/.profile"
        zshenv = self.checkout / "zsh/.zshenv"
        result = self.run_command([
            "zsh", "-dfc",
            '. "$1"; printf "%s" "${SYNTHETIC_LOCAL-unset}"',
            "fixture", str(zshenv),
        ])
        self.assertEqual(result.stdout, "unset")
        local = self.home / ".config/shell/local.env"
        local.parent.mkdir(parents=True)
        local.write_text("export SYNTHETIC_LOCAL=loaded\n")
        result = self.run_command([
            "zsh", "-dfc",
            '. "$1"; . "$2"; . "$2"; printf "%s" "$SYNTHETIC_LOCAL"',
            "fixture", str(profile), str(zshenv),
        ])
        self.assertEqual(result.stdout, "loaded")
        result = self.run_command([
            "sh", "-c", '. "$1"; printf "%s" "$SYNTHETIC_LOCAL"',
            "fixture", str(profile),
        ])
        self.assertEqual(result.stdout, "loaded")

    def test_machine_git_defaults_and_repository_override(self):
        self.stow()
        local = self.home / ".config/git/local"
        local.write_text("[user]\n\tname = Fixture User\n"
                         "\temail = other@example.invalid\n")
        result = self.run_command(["git", "config", "--get", "user.email"])
        self.assertEqual(result.stdout.strip(), "other@example.invalid")
        self.run_command(["git", "init", "--initial-branch=main"])
        self.run_command(["git", "config", "--local", "user.email",
                          "magnusbakken@gmail.com"])
        result = self.run_command(["git", "config", "--get", "user.email"])
        self.assertEqual(result.stdout.strip(), "magnusbakken@gmail.com")
