"""
GitMCP Server - MCP server exposing Git operations as tools for AI agents.

This server provides a comprehensive set of Git operations through the
Model Context Protocol, enabling AI agents to interact with Git repositories
in a safe, structured manner.
"""

import os
import sys
import json
import argparse
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .git_handler import GitHandler


def create_server(allowed_paths: Optional[list[str]] = None) -> FastMCP:
    """
    Create and configure the GitMCP server instance.

    Args:
        allowed_paths: Optional list of allowed root paths for Git operations.

    Returns:
        Configured FastMCP server instance.
    """
    mcp = FastMCP(
        name="GitMCP",
        version="1.0.0",
        instructions=(
            "GitMCP - Git Repository MCP Server. "
            "Provides comprehensive Git operations for AI agents. "
            "Use git_status to check repository state before operations. "
            "All file paths are relative to the repository root."
        ),
    )

    handler = GitHandler(allowed_paths=allowed_paths)

    # ─── Repository Info Tools ───────────────────────────────────────

    @mcp.tool()
    def git_status(repo_path: str) -> str:
        """
        Get the current status of a Git repository.

        Shows current branch, staged/unstaged/untracked files,
        and ahead/behind information.

        Args:
            repo_path: Absolute path to the Git repository.

        Returns:
            JSON string with repository status information.
        """
        status = handler.get_status(repo_path)
        return json.dumps({
            "branch": status.branch,
            "is_clean": status.is_clean,
            "staged_files": status.staged_files,
            "unstaged_files": status.unstaged_files,
            "untracked_files": status.untracked_files,
            "ahead": status.ahead,
            "behind": status.behind,
        }, indent=2, ensure_ascii=False)

    @mcp.tool()
    def git_log(repo_path: str, max_count: int = 20, offset: int = 0) -> str:
        """
        Get commit history of a Git repository.

        Args:
            repo_path: Absolute path to the Git repository.
            max_count: Maximum number of commits to return (default: 20).
            offset: Number of commits to skip (for pagination).

        Returns:
            JSON string with commit history.
        """
        commits = handler.get_log(repo_path, max_count, offset)
        return json.dumps([
            {
                "hash": c.hash,
                "short_hash": c.short_hash,
                "author": c.author,
                "date": c.date,
                "message": c.message,
            }
            for c in commits
        ], indent=2, ensure_ascii=False)

    @mcp.tool()
    def git_branches(repo_path: str) -> str:
        """
        List all branches in a Git repository.

        Args:
            repo_path: Absolute path to the Git repository.

        Returns:
            JSON string with branch information.
        """
        branches = handler.get_branches(repo_path)
        return json.dumps([
            {
                "name": b.name,
                "is_current": b.is_current,
                "is_remote": b.is_remote,
                "tracking": b.tracking,
            }
            for b in branches
        ], indent=2, ensure_ascii=False)

    @mcp.tool()
    def git_tags(repo_path: str) -> str:
        """
        List all tags in a Git repository.

        Args:
            repo_path: Absolute path to the Git repository.

        Returns:
            JSON string with tag names.
        """
        tags = handler.get_tags(repo_path)
        return json.dumps({"tags": tags}, indent=2)

    @mcp.tool()
    def git_remote_url(repo_path: str) -> str:
        """
        Get the remote URL of a Git repository.

        Args:
            repo_path: Absolute path to the Git repository.

        Returns:
            JSON string with remote URL or null.
        """
        url = handler.get_remote_url(repo_path)
        return json.dumps({"remote_url": url}, indent=2)

    # ─── Branch Operations ───────────────────────────────────────────

    @mcp.tool()
    def git_create_branch(repo_path: str, branch_name: str,
                          checkout: bool = True) -> str:
        """
        Create a new branch in the repository.

        Args:
            repo_path: Absolute path to the Git repository.
            branch_name: Name for the new branch.
            checkout: Whether to checkout the new branch (default: true).

        Returns:
            Success message.
        """
        return handler.create_branch(repo_path, branch_name, checkout)

    @mcp.tool()
    def git_checkout(repo_path: str, ref: str) -> str:
        """
        Checkout a branch, tag, or commit.

        Args:
            repo_path: Absolute path to the Git repository.
            ref: Branch name, tag, or commit hash to checkout.

        Returns:
            Success message.
        """
        return handler.checkout(repo_path, ref)

    # ─── Staging & Committing ────────────────────────────────────────

    @mcp.tool()
    def git_add(repo_path: str, files: Optional[str] = None) -> str:
        """
        Stage files for commit.

        Args:
            repo_path: Absolute path to the Git repository.
            files: Comma-separated list of file paths to stage.
                   If empty or null, stages all changes.

        Returns:
            Success message with count of staged files.
        """
        file_list = None
        if files:
            file_list = [f.strip() for f in files.split(",") if f.strip()]
        return handler.add_files(repo_path, file_list)

    @mcp.tool()
    def git_commit(repo_path: str, message: str,
                   allow_empty: bool = False) -> str:
        """
        Create a new commit with staged changes.

        Args:
            repo_path: Absolute path to the Git repository.
            message: Commit message.
            allow_empty: Allow creating an empty commit (default: false).

        Returns:
            Git output from the commit command.
        """
        return handler.commit(repo_path, message, allow_empty)

    # ─── Diff & Changes ──────────────────────────────────────────────

    @mcp.tool()
    def git_diff(repo_path: str, staged: bool = False,
                 file_path: Optional[str] = None) -> str:
        """
        Show differences in the repository.

        Args:
            repo_path: Absolute path to the Git repository.
            staged: Show staged changes (default: false).
            file_path: Optional path to a specific file to diff.

        Returns:
            Unified diff output.
        """
        return handler.diff(repo_path, staged, file_path)

    # ─── File Operations ─────────────────────────────────────────────

    @mcp.tool()
    def git_read_file(repo_path: str, file_path: str,
                      ref: Optional[str] = None) -> str:
        """
        Read a file from the repository.

        Args:
            repo_path: Absolute path to the Git repository.
            file_path: Path to the file relative to repo root.
            ref: Optional git reference (branch/tag/commit) to read from.

        Returns:
            File content as string.
        """
        return handler.read_file(repo_path, file_path, ref)

    @mcp.tool()
    def git_write_file(repo_path: str, file_path: str, content: str) -> str:
        """
        Write content to a file in the repository.

        Creates parent directories if needed. Does NOT auto-stage.

        Args:
            repo_path: Absolute path to the Git repository.
            file_path: Path to the file relative to repo root.
            content: Content to write to the file.

        Returns:
            Success message with byte count.
        """
        return handler.write_file(repo_path, file_path, content)

    @mcp.tool()
    def git_list_files(repo_path: str, directory: str = "",
                       ref: Optional[str] = None) -> str:
        """
        List files in the repository.

        Args:
            repo_path: Absolute path to the Git repository.
            directory: Optional subdirectory to list.
            ref: Optional git reference to list files from.

        Returns:
            JSON string with list of file paths.
        """
        files = handler.list_files(repo_path, directory, ref)
        return json.dumps({"files": files, "count": len(files)}, indent=2)

    @mcp.tool()
    def git_file_info(repo_path: str, file_path: str) -> str:
        """
        Get detailed information about a file.

        Args:
            repo_path: Absolute path to the Git repository.
            file_path: Path to the file relative to repo root.

        Returns:
            JSON string with file information.
        """
        info = handler.get_file_info(repo_path, file_path)
        return json.dumps({
            "path": info.path,
            "status": info.status,
            "staged": info.staged,
        }, indent=2)

    @mcp.tool()
    def git_search_files(repo_path: str, pattern: str,
                         file_pattern: Optional[str] = None) -> str:
        """
        Search for a text pattern in repository files using git grep.

        Args:
            repo_path: Absolute path to the Git repository.
            pattern: Text pattern to search for.
            file_pattern: Optional file glob pattern to filter files.

        Returns:
            JSON string with matching file paths.
        """
        files = handler.search_files(repo_path, pattern, file_pattern)
        return json.dumps({"matches": files, "count": len(files)}, indent=2)

    # ─── Repository Management ───────────────────────────────────────

    @mcp.tool()
    def git_init(repo_path: str) -> str:
        """
        Initialize a new Git repository.

        Args:
            repo_path: Path where the new repository will be created.

        Returns:
            Success message.
        """
        return handler.init_repo(repo_path)

    @mcp.tool()
    def git_clone(repo_path: str, url: str,
                  branch: Optional[str] = None) -> str:
        """
        Clone a remote Git repository.

        Args:
            repo_path: Local path for the cloned repository.
            url: Remote repository URL.
            branch: Optional branch to checkout.

        Returns:
            Success message.
        """
        return handler.clone_repo(repo_path, url, branch)

    # ─── Remote Operations ───────────────────────────────────────────

    @mcp.tool()
    def git_push(repo_path: str, remote: str = "origin",
                 branch: Optional[str] = None,
                 set_upstream: bool = False) -> str:
        """
        Push commits to a remote repository.

        Args:
            repo_path: Absolute path to the Git repository.
            remote: Remote name (default: 'origin').
            branch: Optional branch to push.
            set_upstream: Set upstream tracking (default: false).

        Returns:
            Git push output.
        """
        return handler.push(repo_path, remote, branch, set_upstream)

    @mcp.tool()
    def git_pull(repo_path: str, remote: str = "origin",
                 branch: Optional[str] = None) -> str:
        """
        Pull changes from a remote repository.

        Args:
            repo_path: Absolute path to the Git repository.
            remote: Remote name (default: 'origin').
            branch: Optional branch to pull.

        Returns:
            Git pull output.
        """
        return handler.pull(repo_path, remote, branch)

    # ─── Stash Operations ────────────────────────────────────────────

    @mcp.tool()
    def git_stash(repo_path: str, message: Optional[str] = None) -> str:
        """
        Stash current changes.

        Args:
            repo_path: Absolute path to the Git repository.
            message: Optional stash message.

        Returns:
            Git stash output.
        """
        return handler.stash(repo_path, message)

    @mcp.tool()
    def git_stash_pop(repo_path: str, index: int = 0) -> str:
        """
        Pop a stash entry and apply changes.

        Args:
            repo_path: Absolute path to the Git repository.
            index: Stash index (default: 0).

        Returns:
            Git stash pop output.
        """
        return handler.stash_pop(repo_path, index)

    @mcp.tool()
    def git_stash_list(repo_path: str) -> str:
        """
        List all stash entries.

        Args:
            repo_path: Absolute path to the Git repository.

        Returns:
            JSON string with stash entries.
        """
        entries = handler.stash_list(repo_path)
        return json.dumps({"stashes": entries, "count": len(entries)}, indent=2)

    # ─── Tag Operations ──────────────────────────────────────────────

    @mcp.tool()
    def git_create_tag(repo_path: str, tag_name: str,
                       message: Optional[str] = None) -> str:
        """
        Create a new tag.

        Args:
            repo_path: Absolute path to the Git repository.
            tag_name: Name for the new tag.
            message: Optional tag message (creates annotated tag).

        Returns:
            Success message.
        """
        return handler.tag(repo_path, tag_name, message)

    # ─── History Operations ──────────────────────────────────────────

    @mcp.tool()
    def git_revert(repo_path: str, ref: str) -> str:
        """
        Revert a commit, creating a new commit that undoes the changes.

        Args:
            repo_path: Absolute path to the Git repository.
            ref: Commit hash or reference to revert.

        Returns:
            Git revert output.
        """
        return handler.revert(repo_path, ref)

    @mcp.tool()
    def git_reset(repo_path: str, ref: str, mode: str = "mixed") -> str:
        """
        Reset the current branch to a specific commit.

        Args:
            repo_path: Absolute path to the Git repository.
            ref: Commit hash or reference to reset to.
            mode: Reset mode - 'mixed' (default), 'soft', or 'hard'.

        Returns:
            Git reset output.
        """
        return handler.reset(repo_path, ref, mode)

    # ─── Prompt Resources ────────────────────────────────────────────

    @mcp.resource("gitmcp://help")
    def help_guide() -> str:
        """Get help guide for using GitMCP tools."""
        return """# GitMCP - Git Repository MCP Server

## Available Tools

### Repository Information
- `git_status` - Check repository status (branch, staged/unstaged/untracked files)
- `git_log` - View commit history
- `git_branches` - List all branches
- `git_tags` - List all tags
- `git_remote_url` - Get remote URL

### Branch Operations
- `git_create_branch` - Create a new branch
- `git_checkout` - Switch branches or check out commits

### Staging & Committing
- `git_add` - Stage files for commit
- `git_commit` - Create commits

### File Operations
- `git_read_file` - Read file contents
- `git_write_file` - Write to files
- `git_list_files` - List repository files
- `git_file_info` - Get file status info
- `git_search_files` - Search for text patterns

### Changes & Diff
- `git_diff` - View file differences

### Repository Management
- `git_init` - Initialize new repository
- `git_clone` - Clone remote repository

### Remote Operations
- `git_push` - Push to remote
- `git_pull` - Pull from remote

### Stash Operations
- `git_stash` - Stash changes
- `git_stash_pop` - Apply stashed changes
- `git_stash_list` - List stash entries

### Tag & History
- `git_create_tag` - Create tags
- `git_revert` - Revert commits
- `git_reset` - Reset to commits

## Tips
1. Always run `git_status` first to understand the current state
2. Use `git_add` to stage changes before `git_commit`
3. Use `git_diff` to review changes before committing
4. Use `git_log` to understand commit history
"""

    return mcp


def main():
    """Entry point for the GitMCP server."""
    parser = argparse.ArgumentParser(
        description="GitMCP - Git Repository MCP Server"
    )
    parser.add_argument(
        "--allowed-paths",
        type=str,
        default=None,
        help="Comma-separated list of allowed root paths (security restriction)"
    )
    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        choices=["stdio", "sse"],
        help="Transport type: stdio (default) or sse"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host for SSE transport (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port for SSE transport (default: 8765)"
    )

    args = parser.parse_args()

    allowed = None
    if args.allowed_paths:
        allowed = [p.strip() for p in args.allowed_paths.split(",")]

    server = create_server(allowed_paths=allowed)

    if args.transport == "sse":
        server.run(transport="sse", host=args.host, port=args.port)
    else:
        server.run(transport="stdio")


if __name__ == "__main__":
    main()
