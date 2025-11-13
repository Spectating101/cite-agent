"""
Shell Handler for command execution
Handles shell command execution with safety checks
"""

import os
import time
import uuid
from typing import Dict, Any, Optional


class ShellHandler:
    """
    Handles shell command execution with safety features

    Features:
    - Command execution with timeout
    - Safety classification (SAFE/WRITE/DANGEROUS/BLOCKED)
    - Command output formatting
    - Natural language prefix removal
    """

    def looks_like_user_prompt(self, command: str) -> bool:
        """Check if command looks like a prompt to user rather than actual command"""
        command_lower = command.strip().lower()
        if not command_lower:
            return True
        phrases = [
            "ask the user",
            "can you run",
            "please run",
            "tell the user",
            "ask them",
        ]
        return any(phrase in command_lower for phrase in phrases)

    def infer_shell_command(self, question: str) -> str:
        """Infer shell command from natural language question"""
        question_lower = question.lower()
        if any(word in question_lower for word in ["list", "show", "files", "directory", "folder", "ls"]):
            return "ls -lah"
        if any(word in question_lower for word in ["where", "pwd", "current directory", "location"]):
            return "pwd"
        if "read" in question_lower and any(ext in question_lower for ext in [".py", ".txt", ".csv", "file"]):
            return "ls -lah"
        return "pwd"

    def execute_command(self, command: str, shell_session, is_windows: bool = False) -> str:
        """
        Execute shell command and return output

        Args:
            command: Shell command to execute
            shell_session: Popen object for shell session
            is_windows: Whether running on Windows

        Returns:
            Command output or error message
        """
        try:
            if shell_session is None:
                return "ERROR: Shell session not initialized"

            # Clean command - remove natural language prefixes
            command = command.strip()
            prefixes_to_remove = [
                'run this bash:', 'execute this:', 'run command:', 'execute:',
                'run this:', 'run:', 'bash:', 'command:', 'this bash:', 'this:',
                'r code to', 'R code to', 'python code to', 'in r:', 'in R:',
                'in python:', 'in bash:', 'with r:', 'with bash:'
            ]
            for prefix in prefixes_to_remove:
                if command.lower().startswith(prefix.lower()):
                    command = command[len(prefix):].strip()
                    # Try again in case of nested prefixes
                    for prefix2 in prefixes_to_remove:
                        if command.lower().startswith(prefix2.lower()):
                            command = command[len(prefix2):].strip()
                            break
                    break

            # Use echo markers to detect when command is done
            marker = f"CMD_DONE_{uuid.uuid4().hex[:8]}"

            # Send command with marker
            terminator = "\r\n" if is_windows else "\n"
            if is_windows:
                full_command = f"{command}; echo '{marker}'{terminator}"
            else:
                full_command = f"{command}; echo '{marker}'{terminator}"
            shell_session.stdin.write(full_command)
            shell_session.stdin.flush()

            # Read until we see the marker
            output_lines = []
            start_time = time.time()
            timeout = 30  # Increased for R scripts

            while time.time() - start_time < timeout:
                try:
                    line = shell_session.stdout.readline()
                    if not line:
                        break

                    line = line.rstrip()

                    # Check if we hit the marker
                    if marker in line:
                        break

                    output_lines.append(line)
                except Exception:
                    break

            output = '\n'.join(output_lines).strip()
            debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"

            # Log execution details in debug mode
            if debug_mode:
                output_preview = output[:200] if output else "(no output)"
                print(f"✅ Command executed: {command}")
                print(f"📤 Output ({len(output)} chars): {output_preview}...")

            return output if output else "Command executed (no output)"

        except Exception as e:
            debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
            if debug_mode:
                print(f"❌ Command failed: {command}")
                print(f"❌ Error: {e}")
            return f"ERROR: {e}"

    def format_shell_output(self, output: str, command: str) -> Dict[str, Any]:
        """
        Format shell command output for display

        Args:
            output: Raw command output
            command: The command that was executed

        Returns:
            Dict with formatted preview and metadata
        """
        lines = output.split('\n') if output else []

        # Detect output type based on command
        command_lower = command.lower()

        formatted = {
            "type": "shell_output",
            "command": command,
            "line_count": len(lines),
            "byte_count": len(output),
            "preview": '\n'.join(lines[:10]) if lines else "(no output)",
            "full_output": output
        }

        # Enhanced formatting based on command type
        if any(cmd in command_lower for cmd in ['ls', 'dir']):
            formatted["type"] = "directory_listing"
            formatted["preview"] = f"📁 Found {len([l for l in lines if l.strip()])} items"
        elif any(cmd in command_lower for cmd in ['find', 'locate', 'search']):
            formatted["type"] = "search_results"
            formatted["preview"] = f"🔍 Found {len([l for l in lines if l.strip()])} matches"
        elif any(cmd in command_lower for cmd in ['grep', 'match']):
            formatted["type"] = "search_results"
            formatted["preview"] = f"🔍 Found {len([l for l in lines if l.strip()])} matching lines"
        elif any(cmd in command_lower for cmd in ['cat', 'head', 'tail']):
            formatted["type"] = "file_content"
            formatted["preview"] = f"📄 {len(lines)} lines of content"
        elif any(cmd in command_lower for cmd in ['pwd', 'cd']):
            formatted["type"] = "directory_change"
            formatted["preview"] = f"📍 {output.strip()}"
        elif any(cmd in command_lower for cmd in ['mkdir', 'touch', 'create']):
            formatted["type"] = "file_creation"
            formatted["preview"] = f"✨ Created: {output.strip()}"

        return formatted

    def classify_command_safety(self, cmd: str) -> str:
        """
        Classify command by safety level

        Args:
            cmd: Shell command to classify

        Returns:
            'SAFE', 'WRITE', 'DANGEROUS', or 'BLOCKED'
        """
        cmd = cmd.strip()
        if not cmd:
            return 'BLOCKED'

        cmd_lower = cmd.lower()
        cmd_parts = cmd.split()
        cmd_base = cmd_parts[0] if cmd_parts else ''
        cmd_with_sub = ' '.join(cmd_parts[:2]) if len(cmd_parts) >= 2 else ''

        # BLOCKED: Catastrophic commands
        nuclear_patterns = [
            'rm -rf /',
            'rm -rf ~',
            'rm -rf /*',
            'dd if=/dev/zero',
            'mkfs',
            'fdisk',
            ':(){ :|:& };:',  # Fork bomb
            'chmod -r 777 /',
            '> /dev/sda',
        ]
        for pattern in nuclear_patterns:
            if pattern in cmd_lower:
                return 'BLOCKED'

        # SAFE: Read-only commands
        safe_commands = {
            'pwd', 'ls', 'cd', 'cat', 'head', 'tail', 'grep', 'find', 'which', 'type',
            'wc', 'diff', 'echo', 'ps', 'top', 'df', 'du', 'file', 'stat', 'tree',
            'whoami', 'hostname', 'date', 'cal', 'uptime', 'printenv', 'env',
        }
        safe_git = {'git status', 'git log', 'git diff', 'git branch', 'git show', 'git remote'}

        if cmd_base in safe_commands or cmd_with_sub in safe_git:
            return 'SAFE'

        # WRITE: File creation/modification (allowed but tracked)
        write_commands = {'mkdir', 'touch', 'cp', 'mv', 'tee'}
        if cmd_base in write_commands:
            return 'WRITE'

        # WRITE: Redirection operations (echo > file, cat > file)
        if '>' in cmd or '>>' in cmd:
            # Allow redirection to regular files, block to devices
            if '/dev/' not in cmd_lower:
                return 'WRITE'
            else:
                return 'BLOCKED'

        # DANGEROUS: Deletion and permission changes
        dangerous_commands = {'rm', 'rmdir', 'chmod', 'chown', 'chgrp'}
        if cmd_base in dangerous_commands:
            return 'DANGEROUS'

        # WRITE: Git write operations
        write_git = {'git add', 'git commit', 'git push', 'git pull', 'git checkout', 'git merge'}
        if cmd_with_sub in write_git:
            return 'WRITE'

        # Default: Treat unknown commands as requiring user awareness
        return 'WRITE'

    def is_safe_shell_command(self, cmd: str) -> bool:
        """
        Compatibility wrapper for old safety check

        Args:
            cmd: Shell command to check

        Returns:
            True if safe to execute (SAFE or WRITE level)
        """
        classification = self.classify_command_safety(cmd)
        return classification in ['SAFE', 'WRITE']  # Allow SAFE and WRITE, block DANGEROUS and BLOCKED
