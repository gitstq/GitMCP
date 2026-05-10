"""
Tests for GitMCP - Git operations handler tests.
"""

import os
import sys
import subprocess
from pathlib import Path
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from gitmcp.git_handler import GitHandler


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary Git repository for testing."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    # Initialize git repo
    subprocess.run(
        ["git", "init"],
        cwd=str(repo_path),
        capture_output=True,
        check=True
    )

    # Configure git user
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(repo_path),
        capture_output=True,
        check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(repo_path),
        capture_output=True,
        check=True
    )

    # Create initial commit
    (repo_path / "README.md").write_text("# Test Repo\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=str(repo_path),
        capture_output=True,
        check=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=str(repo_path),
        capture_output=True,
        check=True
    )

    return repo_path


class TestGitHandler:
    """Test suite for GitHandler."""

    def test_validate_path_valid(self, temp_repo):
        """Test path validation with valid repo."""
        handler = GitHandler()
        path = handler._validate_path(str(temp_repo))
        assert path.exists()

    def test_validate_path_not_exists(self):
        """Test path validation with non-existent path."""
        handler = GitHandler()
        with pytest.raises(FileNotFoundError):
            handler._validate_path("/nonexistent/path/repo")

    def test_validate_path_not_git_repo(self, tmp_path):
        """Test path validation with non-git directory."""
        handler = GitHandler()
        non_git = tmp_path / "not_a_repo"
        non_git.mkdir()
        with pytest.raises(ValueError):
            handler._validate_path(str(non_git))

    def test_validate_path_allowed_paths(self, temp_repo):
        """Test path validation with allowed paths restriction."""
        handler = GitHandler(allowed_paths=[str(temp_repo)])
        path = handler._validate_path(str(temp_repo))
        assert path.exists()

    def test_validate_path_blocked(self, temp_repo, tmp_path):
        """Test path validation blocks unauthorized paths."""
        handler = GitHandler(allowed_paths=[str(tmp_path / "other")])
        with pytest.raises(PermissionError):
            handler._validate_path(str(temp_repo))

    def test_get_status(self, temp_repo):
        """Test getting repository status."""
        handler = GitHandler()
        status = handler.get_status(str(temp_repo))

        assert status.branch in ("main", "master")
        assert status.is_clean is True
        assert len(status.staged_files) == 0
        assert len(status.untracked_files) == 0

    def test_get_status_with_changes(self, temp_repo):
        """Test status with uncommitted changes."""
        handler = GitHandler()

        # Create untracked file
        (temp_repo / "new_file.txt").write_text("new content")

        status = handler.get_status(str(temp_repo))
        assert status.is_clean is False
        assert len(status.untracked_files) > 0

    def test_get_log(self, temp_repo):
        """Test getting commit log."""
        handler = GitHandler()
        commits = handler.get_log(str(temp_repo))

        assert len(commits) >= 1
        assert commits[0].message == "Initial commit"
        assert commits[0].author == "Test User"

    def test_get_log_pagination(self, temp_repo):
        """Test commit log pagination."""
        handler = GitHandler()

        # Create more commits
        for i in range(5):
            (temp_repo / f"file_{i}.txt").write_text(f"content {i}")
            subprocess.run(
                ["git", "add", "."],
                cwd=str(temp_repo),
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["git", "commit", "-m", f"Commit {i}"],
                cwd=str(temp_repo),
                capture_output=True,
                check=True
            )

        # Get first page
        page1 = handler.get_log(str(temp_repo), max_count=3)
        assert len(page1) == 3

        # Get second page
        page2 = handler.get_log(str(temp_repo), max_count=3, offset=3)
        assert len(page2) == 3

        # Ensure no overlap
        page1_hashes = {c.hash for c in page1}
        page2_hashes = {c.hash for c in page2}
        assert len(page1_hashes & page2_hashes) == 0

    def test_get_branches(self, temp_repo):
        """Test listing branches."""
        handler = GitHandler()
        branches = handler.get_branches(str(temp_repo))

        assert len(branches) >= 1
        current = [b for b in branches if b.is_current]
        assert len(current) == 1

    def test_create_branch(self, temp_repo):
        """Test creating a new branch."""
        handler = GitHandler()
        result = handler.create_branch(str(temp_repo), "feature/test")

        assert "created" in result.lower() or "feature/test" in result

        branches = handler.get_branches(str(temp_repo))
        branch_names = [b.name for b in branches]
        assert "feature/test" in branch_names

    def test_checkout(self, temp_repo):
        """Test checking out a branch."""
        handler = GitHandler()

        # Create and checkout new branch
        handler.create_branch(str(temp_repo), "develop", checkout=True)

        # Get the main branch name
        status = handler.get_status(str(temp_repo))
        main_branch = status.branch  # currently on develop

        # Checkout back to main/master
        branches = handler.get_branches(str(temp_repo))
        main_branch_name = None
        for b in branches:
            if not b.is_current and not b.is_remote and b.name in ("main", "master"):
                main_branch_name = b.name
                break

        if main_branch_name:
            result = handler.checkout(str(temp_repo), main_branch_name)
            assert main_branch_name in result

    def test_add_and_commit(self, temp_repo):
        """Test staging and committing files."""
        handler = GitHandler()

        # Create a new file
        handler.write_file(str(temp_repo), "test.txt", "hello world")

        # Stage and commit
        handler.add_files(str(temp_repo), ["test.txt"])
        result = handler.commit(str(temp_repo), "Add test file")

        assert result  # Should have output

        # Verify in log
        commits = handler.get_log(str(temp_repo), max_count=1)
        assert commits[0].message == "Add test file"

    def test_add_all(self, temp_repo):
        """Test staging all changes."""
        handler = GitHandler()

        handler.write_file(str(temp_repo), "a.txt", "a")
        handler.write_file(str(temp_repo), "b.txt", "b")

        result = handler.add_files(str(temp_repo))
        assert "all" in result.lower() or "staged" in result.lower()

    def test_diff(self, temp_repo):
        """Test showing diff."""
        handler = GitHandler()

        # Modify a file
        handler.write_file(str(temp_repo), "README.md", "# Modified\n")

        diff = handler.diff(str(temp_repo))
        assert "Modified" in diff or "README" in diff

    def test_diff_staged(self, temp_repo):
        """Test showing staged diff."""
        handler = GitHandler()

        handler.write_file(str(temp_repo), "README.md", "# Staged\n")
        handler.add_files(str(temp_repo), ["README.md"])

        diff = handler.diff(str(temp_repo), staged=True)
        assert "Staged" in diff or "README" in diff

    def test_read_file(self, temp_repo):
        """Test reading a file."""
        handler = GitHandler()
        content = handler.read_file(str(temp_repo), "README.md")
        assert "Test Repo" in content

    def test_write_file(self, temp_repo):
        """Test writing a file."""
        handler = GitHandler()
        result = handler.write_file(str(temp_repo), "output.txt", "test content")

        assert "output.txt" in result
        assert "test content" == (temp_repo / "output.txt").read_text()

    def test_write_file_nested(self, temp_repo):
        """Test writing to nested directory."""
        handler = GitHandler()
        result = handler.write_file(str(temp_repo), "src/module/main.py", "# main")

        assert "src/module/main.py" in result
        assert (temp_repo / "src" / "module" / "main.py").exists()

    def test_list_files(self, temp_repo):
        """Test listing files."""
        handler = GitHandler()
        result = handler.list_files(str(temp_repo))

        assert "README.md" in result

    def test_list_files_with_directory(self, temp_repo):
        """Test listing files in subdirectory."""
        handler = GitHandler()

        # Create nested files
        handler.write_file(str(temp_repo), "src/a.py", "a")
        handler.write_file(str(temp_repo), "src/b.py", "b")
        handler.write_file(str(temp_repo), "docs/readme.md", "docs")

        files = handler.list_files(str(temp_repo), directory="src")
        assert all("src/" in f for f in files)
        assert len(files) == 2

    def test_file_info(self, temp_repo):
        """Test getting file info."""
        handler = GitHandler()
        info = handler.get_file_info(str(temp_repo), "README.md")

        assert info.path == "README.md"
        assert info.status in ("unmodified", "staged", "modified")

    def test_search_files(self, temp_repo):
        """Test searching files."""
        handler = GitHandler()
        results = handler.search_files(str(temp_repo), "Test Repo")

        assert len(results) > 0
        assert any("README" in r for r in results)

    def test_init_repo(self, tmp_path):
        """Test initializing a new repository."""
        handler = GitHandler()
        new_repo = str(tmp_path / "new_repo")

        result = handler.init_repo(new_repo)
        assert "Initialized" in result
        assert os.path.exists(os.path.join(new_repo, ".git"))

    def test_tag_operations(self, temp_repo):
        """Test creating and listing tags."""
        handler = GitHandler()

        handler.tag(str(temp_repo), "v1.0.0", "Version 1.0.0")
        tags = handler.get_tags(str(temp_repo))

        assert "v1.0.0" in tags

    def test_stash_operations(self, temp_repo):
        """Test stash operations."""
        handler = GitHandler()

        # Create changes and stage them (stash requires tracked changes)
        handler.write_file(str(temp_repo), "README.md", "# Modified for stash\n")
        handler.add_files(str(temp_repo), ["README.md"])

        # Stash
        handler.stash(str(temp_repo), "test stash")

        # List stashes
        stashes = handler.stash_list(str(temp_repo))
        assert len(stashes) > 0

        # Pop stash
        handler.stash_pop(str(temp_repo))

        # Verify file restored
        content = handler.read_file(str(temp_repo), "README.md")
        assert "Modified for stash" in content

    def test_revert(self, temp_repo):
        """Test reverting a commit."""
        handler = GitHandler()

        # Create a commit to revert
        handler.write_file(str(temp_repo), "revert_me.txt", "will be reverted")
        handler.add_files(str(temp_repo), ["revert_me.txt"])
        handler.commit(str(temp_repo), "Commit to revert")

        # Get the commit hash
        commits = handler.get_log(str(temp_repo), max_count=1)
        commit_hash = commits[0].hash

        # Revert
        result = handler.revert(str(temp_repo), commit_hash)
        assert result  # Should have output

    def test_reset(self, temp_repo):
        """Test resetting to a commit."""
        handler = GitHandler()

        # Get initial commit
        commits = handler.get_log(str(temp_repo), max_count=10)
        initial_hash = commits[-1].hash

        # Create new commits
        handler.write_file(str(temp_repo), "reset_me.txt", "content")
        handler.add_files(str(temp_repo), ["reset_me.txt"])
        handler.commit(str(temp_repo), "Will be reset")

        # Soft reset
        handler.reset(str(temp_repo), initial_hash, mode="soft")

    def test_get_remote_url_no_remote(self, temp_repo):
        """Test getting remote URL when no remote is set."""
        handler = GitHandler()
        url = handler.get_remote_url(str(temp_repo))
        assert url is None

    def test_get_remote_url_with_remote(self, temp_repo):
        """Test getting remote URL."""
        handler = GitHandler()

        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/test/repo.git"],
            cwd=str(temp_repo),
            capture_output=True,
            check=True
        )

        url = handler.get_remote_url(str(temp_repo))
        assert url == "https://github.com/test/repo.git"

    def test_read_file_at_ref(self, temp_repo):
        """Test reading a file at a specific commit."""
        handler = GitHandler()

        # Modify file and commit
        handler.write_file(str(temp_repo), "README.md", "# Updated\n")
        handler.add_files(str(temp_repo), ["README.md"])
        handler.commit(str(temp_repo), "Update README")

        # Get the initial commit hash
        commits = handler.get_log(str(temp_repo), max_count=10)
        initial_hash = commits[-1].hash

        # Read file at initial commit
        content = handler.read_file(str(temp_repo), "README.md", ref=initial_hash)
        assert "Test Repo" in content

    def test_list_files_at_ref(self, temp_repo):
        """Test listing files at a specific commit."""
        handler = GitHandler()

        # Get initial commit hash
        commits = handler.get_log(str(temp_repo), max_count=10)
        initial_hash = commits[-1].hash

        # Add more files
        handler.write_file(str(temp_repo), "later.txt", "added later")
        handler.add_files(str(temp_repo), ["later.txt"])
        handler.commit(str(temp_repo), "Add later file")

        # List files at initial commit
        files = handler.list_files(str(temp_repo), ref=initial_hash)
        assert "README.md" in files
        assert "later.txt" not in files


class TestGitHandlerEdgeCases:
    """Edge case tests."""

    def test_empty_repo_status(self, tmp_path):
        """Test status of empty repo with no commits."""
        repo = tmp_path / "empty"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=str(repo), capture_output=True, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=str(repo), capture_output=True, check=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=str(repo), capture_output=True, check=True
        )

        handler = GitHandler()
        status = handler.get_status(str(repo))
        assert status.branch == "" or status.branch is not None

    def test_unicode_file_content(self, temp_repo):
        """Test reading/writing Unicode content."""
        handler = GitHandler()

        unicode_content = "你好世界 🌍 Héllo Wörld"
        handler.write_file(str(temp_repo), "unicode.txt", unicode_content)
        read_back = handler.read_file(str(temp_repo), "unicode.txt")

        assert read_back == unicode_content

    def test_large_file_content(self, temp_repo):
        """Test reading/writing large files."""
        handler = GitHandler()

        large_content = "line\n" * 10000
        result = handler.write_file(str(temp_repo), "large.txt", large_content)
        assert "10000" in result or "bytes" in result.lower()

    def test_nonexistent_file_read(self, temp_repo):
        """Test reading non-existent file raises error."""
        handler = GitHandler()
        with pytest.raises(FileNotFoundError):
            handler.read_file(str(temp_repo), "nonexistent.txt")

    def test_nonexistent_file_info(self, temp_repo):
        """Test getting info for non-existent file raises error."""
        handler = GitHandler()
        with pytest.raises(FileNotFoundError):
            handler.get_file_info(str(temp_repo), "nonexistent.txt")

    def test_invalid_reset_mode(self, temp_repo):
        """Test that invalid reset mode raises error."""
        handler = GitHandler()
        with pytest.raises(ValueError):
            handler.reset(str(temp_repo), "HEAD", mode="invalid")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
