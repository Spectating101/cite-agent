"""
File Operations Handler
Handles read, write, edit, glob, and grep operations
"""

import os
import re
import glob as glob_module
from typing import Dict, Any, List, Optional


class FileOperations:
    """
    Handles all file operations for EnhancedNocturnalAgent

    Operations:
    - read_file() - Read file with line numbers
    - write_file() - Write/create file
    - edit_file() - Surgical string replacement
    - glob_search() - Pattern-based file search
    - grep_search() - Content search across files
    - batch_edit_files() - Multi-file edits
    """

    def read_file(self, file_path: str, offset: int = 0, limit: int = 2000,
                  file_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Read file with line numbers (like Claude Code's Read tool)

        Args:
            file_path: Path to file
            offset: Starting line number (0-indexed)
            limit: Maximum number of lines to read
            file_context: Optional file context dict to update

        Returns:
            File contents with line numbers in format: "  123→content"
        """
        try:
            # Expand ~ to home directory
            file_path = os.path.expanduser(file_path)

            # Make absolute if relative
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)

            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()

            # Apply offset and limit
            if offset or limit:
                lines = lines[offset:offset+limit if limit else None]

            # Format with line numbers (1-indexed, like vim/editors)
            numbered_lines = [
                f"{offset+i+1:6d}→{line.rstrip()}\n"
                for i, line in enumerate(lines)
            ]

            result = ''.join(numbered_lines)

            # Update file context if provided
            if file_context is not None:
                file_context['last_file'] = file_path
                if file_path not in file_context.get('recent_files', []):
                    if 'recent_files' not in file_context:
                        file_context['recent_files'] = []
                    file_context['recent_files'].append(file_path)
                    file_context['recent_files'] = file_context['recent_files'][-5:]

            return result if result else "(empty file)"

        except FileNotFoundError:
            return f"ERROR: File not found: {file_path}"
        except PermissionError:
            return f"ERROR: Permission denied: {file_path}"
        except IsADirectoryError:
            return f"ERROR: {file_path} is a directory, not a file"
        except Exception as e:
            return f"ERROR: {type(e).__name__}: {e}"

    def write_file(self, file_path: str, content: str,
                   file_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Write file directly (like Claude Code's Write tool)
        Creates new file or overwrites existing one.

        Args:
            file_path: Path to file
            content: Full file content
            file_context: Optional file context dict to update

        Returns:
            {"success": bool, "message": str, "bytes_written": int}
        """
        try:
            # Expand ~ to home directory
            file_path = os.path.expanduser(file_path)

            # Make absolute if relative
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)

            # Create parent directories if needed
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                bytes_written = f.write(content)

            # Update file context if provided
            if file_context is not None:
                file_context['last_file'] = file_path
                if file_path not in file_context.get('recent_files', []):
                    if 'recent_files' not in file_context:
                        file_context['recent_files'] = []
                    file_context['recent_files'].append(file_path)
                    file_context['recent_files'] = file_context['recent_files'][-5:]

            return {
                "success": True,
                "message": f"Wrote {bytes_written} bytes to {file_path}",
                "bytes_written": bytes_written
            }

        except PermissionError:
            return {
                "success": False,
                "message": f"ERROR: Permission denied: {file_path}",
                "bytes_written": 0
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"ERROR: {type(e).__name__}: {e}",
                "bytes_written": 0
            }

    def edit_file(self, file_path: str, old_string: str, new_string: str,
                  replace_all: bool = False,
                  file_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Surgical file edit (like Claude Code's Edit tool)

        Args:
            file_path: Path to file
            old_string: Exact string to replace (must be unique unless replace_all=True)
            new_string: Replacement string
            replace_all: If True, replace all occurrences
            file_context: Optional file context dict to update

        Returns:
            {"success": bool, "message": str, "replacements": int}
        """
        try:
            # Expand ~ to home directory
            file_path = os.path.expanduser(file_path)

            # Make absolute if relative
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)

            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for uniqueness if not replace_all
            occurrences = content.count(old_string)
            if occurrences == 0:
                return {
                    "success": False,
                    "message": f"ERROR: String not found in {file_path}",
                    "replacements": 0
                }

            if not replace_all and occurrences > 1:
                return {
                    "success": False,
                    "message": f"ERROR: String appears {occurrences} times in {file_path}. Use replace_all=True or make old_string more specific.",
                    "replacements": 0
                }

            # Perform replacement
            if replace_all:
                new_content = content.replace(old_string, new_string)
            else:
                new_content = content.replace(old_string, new_string, 1)

            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # Update file context if provided
            if file_context is not None:
                file_context['last_file'] = file_path

            return {
                "success": True,
                "message": f"Replaced {occurrences if replace_all else 1} occurrence(s) in {file_path}",
                "replacements": occurrences if replace_all else 1
            }

        except FileNotFoundError:
            return {
                "success": False,
                "message": f"ERROR: File not found: {file_path}",
                "replacements": 0
            }
        except PermissionError:
            return {
                "success": False,
                "message": f"ERROR: Permission denied: {file_path}",
                "replacements": 0
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"ERROR: {type(e).__name__}: {e}",
                "replacements": 0
            }

    def glob_search(self, pattern: str, path: str = ".") -> Dict[str, Any]:
        """
        Fast file pattern matching (like Claude Code's Glob tool)

        Args:
            pattern: Glob pattern (e.g., "*.py", "**/*.md", "src/**/*.ts")
            path: Starting directory (default: current directory)

        Returns:
            {"files": List[str], "count": int, "pattern": str}
        """
        try:
            # Expand ~ to home directory
            path = os.path.expanduser(path)

            # Make absolute if relative
            if not os.path.isabs(path):
                path = os.path.abspath(path)

            # Combine path and pattern
            full_pattern = os.path.join(path, pattern)

            # Find matches (recursive if ** in pattern)
            matches = glob_module.glob(full_pattern, recursive=True)

            # Filter to files only (not directories)
            files = [f for f in matches if os.path.isfile(f)]

            # Sort by modification time (newest first)
            files.sort(key=lambda f: os.path.getmtime(f), reverse=True)

            return {
                "files": files,
                "count": len(files),
                "pattern": full_pattern
            }

        except Exception as e:
            return {
                "files": [],
                "count": 0,
                "pattern": pattern,
                "error": f"{type(e).__name__}: {e}"
            }

    def grep_search(self, pattern: str, path: str = ".",
                    file_pattern: str = "*",
                    output_mode: str = "files_with_matches",
                    context_lines: int = 0,
                    ignore_case: bool = False,
                    max_results: int = 100) -> Dict[str, Any]:
        """
        Fast content search (like Claude Code's Grep tool / ripgrep)

        Args:
            pattern: Regex pattern to search for
            path: Directory to search in
            file_pattern: Glob pattern for files to search (e.g., "*.py")
            output_mode: "files_with_matches", "content", or "count"
            context_lines: Lines of context around matches
            ignore_case: Case-insensitive search
            max_results: Maximum number of results to return

        Returns:
            Depends on output_mode:
            - files_with_matches: {"files": List[str], "count": int}
            - content: {"matches": {file: [(line_num, line_content), ...]}}
            - count: {"counts": {file: match_count}}
        """
        try:
            # Expand ~ to home directory
            path = os.path.expanduser(path)

            # Make absolute if relative
            if not os.path.isabs(path):
                path = os.path.abspath(path)

            # Compile regex
            flags = re.IGNORECASE if ignore_case else 0
            regex = re.compile(pattern, flags)

            # Find files to search
            glob_result = self.glob_search(file_pattern, path)
            files_to_search = glob_result["files"]

            # Search each file
            if output_mode == "files_with_matches":
                matching_files = []
                for file_path in files_to_search[:max_results]:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                        if regex.search(content):
                            matching_files.append(file_path)
                    except:
                        continue

                return {
                    "files": matching_files,
                    "count": len(matching_files),
                    "pattern": pattern
                }

            elif output_mode == "content":
                matches = {}
                for file_path in files_to_search:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            lines = f.readlines()

                        file_matches = []
                        for line_num, line in enumerate(lines, 1):
                            if regex.search(line):
                                file_matches.append((line_num, line.rstrip()))

                                if len(file_matches) >= max_results:
                                    break

                        if file_matches:
                            matches[file_path] = file_matches
                    except:
                        continue

                return {
                    "matches": matches,
                    "file_count": len(matches),
                    "pattern": pattern
                }

            elif output_mode == "count":
                counts = {}
                for file_path in files_to_search:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()

                        match_count = len(regex.findall(content))
                        if match_count > 0:
                            counts[file_path] = match_count
                    except:
                        continue

                return {
                    "counts": counts,
                    "total_matches": sum(counts.values()),
                    "pattern": pattern
                }

            else:
                return {
                    "error": f"Invalid output_mode: {output_mode}. Use 'files_with_matches', 'content', or 'count'."
                }

        except re.error as e:
            return {
                "error": f"Invalid regex pattern: {e}"
            }
        except Exception as e:
            return {
                "error": f"{type(e).__name__}: {e}"
            }

    async def batch_edit_files(self, edits: List[Dict[str, str]],
                               file_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Batch edit multiple files (useful for refactoring)

        Args:
            edits: List of {"file": path, "old": old_string, "new": new_string}
            file_context: Optional file context dict to update

        Returns:
            {"success": bool, "results": List[Dict], "total_replacements": int}
        """
        results = []
        total_replacements = 0

        for edit in edits:
            file_path = edit.get("file")
            old_string = edit.get("old")
            new_string = edit.get("new")
            replace_all = edit.get("replace_all", False)

            if not all([file_path, old_string is not None, new_string is not None]):
                results.append({
                    "file": file_path,
                    "success": False,
                    "message": "Missing required fields: file, old, new"
                })
                continue

            result = self.edit_file(file_path, old_string, new_string, replace_all, file_context)
            results.append(result)

            if result["success"]:
                total_replacements += result["replacements"]

        success = all(r.get("success", False) for r in results)

        return {
            "success": success,
            "results": results,
            "total_replacements": total_replacements,
            "files_edited": len([r for r in results if r.get("success")])
        }
