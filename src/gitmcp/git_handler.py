"""
Git operations handler - Wraps GitPython for safe, structured Git operations.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class GitStatus:
    """Represents the current Git repository status."""
    branch: str = ""
    is_clean: bool = True
    staged_files: list[str] = field(default_factory=list)
    unstaged_files: list[str] = field(default_factory=list)
    untracked_files: list[str] = field(default_factory=list)
    ahead: int = 0
    behind: int = 0


@dataclass
class CommitInfo:
    """Represents a Git commit."""
    hash: str = ""
    short_hash: str = ""
    author: str = ""
    date: str = ""
    message: str = ""


@dataclass
class BranchInfo:
    """Represents a Git branch."""
    name: str = ""
    is_current: bool = False
    is_remote: bool = False
    tracking: Optional[str] = None


@dataclass
class FileInfo:
    """Represents a file in the repository."""
    path: str = ""
    status: str = ""
    staged: bool = False


class GitHandler:
    """
    Safe Git operations handler with path validation and sandbox support.
    """

    def __init__(self, allowed_paths: Optional[list[str]] = None):
        """
        Initialize GitHandler.

        Args:
            allowed_paths: List of allowed root paths. None means all paths allowed.
        """
        self.allowed_paths = allowed_paths

    def _validate_path(self, repo_path: str) -> Path:
        """Validate and resolve the repository path."""
        path = Path(repo_path).resolve()

        if self.allowed_paths:
            allowed = [Path(p).resolve() for p in self.allowed_paths]
            if not any(str(path).startswith(str(a)) for a in allowed):
                raise PermissionError(
                    f"Access denied: {path} is not within allowed paths"
                )

        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        if not (path / ".git").exists() and not path.suffix == ".git":
            # Check if it's inside a git repo
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--git-dir"],
                    cwd=str(path),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode != 0:
                    raise ValueError(f"Not a Git repository: {path}")
            except FileNotFoundError:
                raise ValueError("Git is not installed on this system")

        return path

    def _run_git(self, args: list[str], repo_path: Path) -> str:
        """Run a git command and return stdout."""
        result = subprocess.run(
            ["git"] + args,
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git error: {result.stderr.strip()}")
        return result.stdout.strip()

    def get_status(self, repo_path: str) -> GitStatus:
        """Get the current status of a Git repository."""
        path = self._validate_path(repo_path)

        try:
            branch = self._run_git(["branch", "--show-current"], path)
        except RuntimeError:
            branch = self._run_git(["rev-parse", "--short", "HEAD"], path)

        # Get ahead/behind info
        try:
            ab = self._run_git(["rev-list", "--count", "--left-right", "@{upstream}...HEAD"], path)
            if ab:
                parts = ab.split("\t")
                behind = int(parts[0]) if len(parts) > 0 else 0
                ahead = int(parts[1]) if len(parts) > 1 else 0
            else:
                ahead, behind = 0, 0
        except RuntimeError:
            ahead, behind = 0, 0

        # Parse status
        try:
            status_output = self._run_git(["status", "--porcelain=v1"], path)
        except RuntimeError:
            status_output = ""

        staged = []
        unstaged = []
        untracked = []

        for line in status_output.split("\n"):
            if not line:
                continue
            if line.startswith("??"):
                untracked.append(line[3:])
            elif line[0] in "MADRC" and line[1] == " ":
                staged.append(line[3:])
            elif line[0] == " " and line[1] in "MADRC":
                unstaged.append(line[3:])
            elif line[0] in "MADRC" and line[1] in "MADRC":
                staged.append(line[3:])
                unstaged.append(line[3:])

        is_clean = not staged and not unstaged and not untracked

        return GitStatus(
            branch=branch,
            is_clean=is_clean,
            staged_files=staged,
            unstaged_files=unstaged,
            untracked_files=untracked,
            ahead=ahead,
            behind=behind,
        )

    def get_log(self, repo_path: str, max_count: int = 20,
                offset: int = 0) -> list[CommitInfo]:
        """Get commit history."""
        path = self._validate_path(repo_path)

        output = self._run_git([
            "log",
            f"--max-count={max_count}",
            f"--skip={offset}",
            "--format=%H%n%h%n%an%n%ai%n%s%n---SEPARATOR---"
        ], path)

        commits = []
        entries = output.split("---SEPARATOR---")
        for entry in entries:
            lines = entry.strip().split("\n")
            if len(lines) >= 5:
                commits.append(CommitInfo(
                    hash=lines[0],
                    short_hash=lines[1],
                    author=lines[2],
                    date=lines[3],
                    message="\n".join(lines[4:]),
                ))

        return commits

    def get_branches(self, repo_path: str) -> list[BranchInfo]:
        """List all branches."""
        path = self._validate_path(repo_path)

        output = self._run_git([
            "branch", "-a", "--format=%(refname:short)%(HEAD)%(upstream:short)"
        ], path)

        branches = []
        current_branch = self._run_git(["branch", "--show-current"], path)

        for line in output.split("\n"):
            if not line:
                continue
            is_current = line.endswith("*")
            name = line.rstrip("*")

            is_remote = name.startswith("origin/") or name.startswith("remotes/")
            tracking = None
            if "/" in name and not name.startswith("origin/"):
                parts = name.split("/")
                tracking = "/".join(parts[1:])

            branches.append(BranchInfo(
                name=name,
                is_current=is_current,
                is_remote=is_remote,
                tracking=tracking,
            ))

        return branches

    def create_branch(self, repo_path: str, branch_name: str,
                      checkout: bool = True) -> str:
        """Create a new branch."""
        path = self._validate_path(repo_path)

        args = ["checkout", "-b", branch_name] if checkout else ["branch", branch_name]
        self._run_git(args, path)
        return f"Branch '{branch_name}' created successfully"

    def checkout(self, repo_path: str, ref: str) -> str:
        """Checkout a branch or commit."""
        path = self._validate_path(repo_path)
        self._run_git(["checkout", ref], path)
        return f"Checked out '{ref}'"

    def add_files(self, repo_path: str, files: Optional[list[str]] = None) -> str:
        """Stage files for commit."""
        path = self._validate_path(repo_path)

        if files:
            self._run_git(["add"] + files, path)
            return f"Staged {len(files)} file(s)"
        else:
            self._run_git(["add", "."], path)
            return "Staged all changes"

    def commit(self, repo_path: str, message: str,
               allow_empty: bool = False) -> str:
        """Create a commit."""
        path = self._validate_path(repo_path)

        args = ["commit", "-m", message]
        if allow_empty:
            args.append("--allow-empty")

        output = self._run_git(args, path)
        return output

    def diff(self, repo_path: str, staged: bool = False,
             file_path: Optional[str] = None) -> str:
        """Show diff of changes."""
        path = self._validate_path(repo_path)

        args = ["diff"]
        if staged:
            args.append("--staged")
        if file_path:
            args.append(file_path)

        return self._run_git(args, path)

    def read_file(self, repo_path: str, file_path: str,
                  ref: Optional[str] = None) -> str:
        """Read a file from the repository."""
        path = self._validate_path(repo_path)

        full_path = path / file_path
        if ref:
            return self._run_git(["show", f"{ref}:{file_path}"], path)

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        return full_path.read_text(encoding="utf-8", errors="replace")

    def write_file(self, repo_path: str, file_path: str,
                   content: str) -> str:
        """Write content to a file in the repository."""
        path = self._validate_path(repo_path)

        full_path = path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

        return f"Written {len(content)} bytes to {file_path}"

    def list_files(self, repo_path: str, directory: str = "",
                   ref: Optional[str] = None) -> list[str]:
        """List files in the repository."""
        path = self._validate_path(repo_path)

        if ref:
            output = self._run_git(["ls-tree", "-r", "--name-only", ref], path)
            files = [f for f in output.split("\n") if f]
            if directory:
                files = [f for f in files if f.startswith(directory)]
            return files

        target = path / directory if directory else path
        if not target.exists():
            return []

        files = []
        for item in target.rglob("*"):
            if item.is_file():
                rel = str(item.relative_to(path))
                if not rel.startswith(".git"):
                    files.append(rel)

        return sorted(files)

    def get_file_info(self, repo_path: str, file_path: str) -> FileInfo:
        """Get information about a specific file."""
        path = self._validate_path(repo_path)

        full_path = path / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            status = self._run_git(["status", "--porcelain", file_path], path)
            is_staged = False
            file_status = "unmodified"
            if status:
                code = status[:2]
                is_staged = code[0] != " " and code[0] != "?"
                if code.startswith("??"):
                    file_status = "untracked"
                elif code[0] in "MADRC":
                    file_status = "staged"
                elif code[1] in "MADRC":
                    file_status = "modified"
        except RuntimeError:
            file_status = "untracked"
            is_staged = False

        return FileInfo(path=file_path, status=file_status, staged=is_staged)

    def init_repo(self, repo_path: str) -> str:
        """Initialize a new Git repository."""
        path = Path(repo_path).resolve()
        path.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            ["git", "init"],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to initialize repo: {result.stderr}")

        return f"Initialized empty Git repository in {path}"

    def clone_repo(self, repo_path: str, url: str,
                   branch: Optional[str] = None) -> str:
        """Clone a remote repository."""
        parent = Path(repo_path).resolve().parent
        parent.mkdir(parents=True, exist_ok=True)

        args = ["clone", url, str(repo_path)]
        if branch:
            args.extend(["--branch", branch])

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            raise RuntimeError(f"Clone failed: {result.stderr}")

        return f"Cloned {url} to {repo_path}"

    def push(self, repo_path: str, remote: str = "origin",
             branch: Optional[str] = None,
             set_upstream: bool = False) -> str:
        """Push to a remote repository."""
        path = self._validate_path(repo_path)

        args = ["push"]
        if set_upstream:
            args.append("-u")
        args.append(remote)
        if branch:
            args.append(branch)

        return self._run_git(args, path)

    def pull(self, repo_path: str, remote: str = "origin",
             branch: Optional[str] = None) -> str:
        """Pull from a remote repository."""
        path = self._validate_path(repo_path)

        args = ["pull", remote]
        if branch:
            args.append(branch)

        return self._run_git(args, path)

    def stash(self, repo_path: str, message: Optional[str] = None) -> str:
        """Stash current changes."""
        path = self._validate_path(repo_path)

        args = ["stash"]
        if message:
            args.extend(["push", "-m", message])

        return self._run_git(args, path)

    def stash_pop(self, repo_path: str, index: int = 0) -> str:
        """Pop a stash entry."""
        path = self._validate_path(repo_path)
        return self._run_git(["stash", "pop", f"stash@{{{index}}}"], path)

    def stash_list(self, repo_path: str) -> list[str]:
        """List stash entries."""
        path = self._validate_path(repo_path)

        try:
            output = self._run_git(["stash", "list"], path)
            return [line for line in output.split("\n") if line]
        except RuntimeError:
            return []

    def tag(self, repo_path: str, tag_name: str,
            message: Optional[str] = None) -> str:
        """Create a tag."""
        path = self._validate_path(repo_path)

        args = ["tag", tag_name]
        if message:
            args = ["tag", "-a", tag_name, "-m", message]

        self._run_git(args, path)
        return f"Tag '{tag_name}' created"

    def get_tags(self, repo_path: str) -> list[str]:
        """List all tags."""
        path = self._validate_path(repo_path)
        output = self._run_git(["tag", "-l"], path)
        return [t for t in output.split("\n") if t]

    def revert(self, repo_path: str, ref: str) -> str:
        """Revert a commit."""
        path = self._validate_path(repo_path)
        return self._run_git(["revert", ref, "--no-edit"], path)

    def reset(self, repo_path: str, ref: str, mode: str = "mixed") -> str:
        """Reset to a commit."""
        path = self._validate_path(repo_path)
        valid_modes = ["mixed", "soft", "hard"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid reset mode: {mode}. Must be one of {valid_modes}")

        return self._run_git(["reset", f"--{mode}", ref], path)

    def search_files(self, repo_path: str, pattern: str,
                     file_pattern: Optional[str] = None) -> list[str]:
        """Search for a pattern in files using git grep."""
        path = self._validate_path(repo_path)

        args = ["grep", "-l", pattern]
        if file_pattern:
            args.extend(["--", file_pattern])

        try:
            output = self._run_git(args, path)
            return [f for f in output.split("\n") if f]
        except RuntimeError:
            return []

    def get_remote_url(self, repo_path: str) -> Optional[str]:
        """Get the remote URL of the repository."""
        path = self._validate_path(repo_path)

        try:
            return self._run_git(["remote", "get-url", "origin"], path)
        except RuntimeError:
            return None
