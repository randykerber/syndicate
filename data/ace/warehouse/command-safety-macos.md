# macOS Command Safety Verification Rules

*For use as Global Rule in Warp and other AI agents*  
*Last updated: 2026-01-02*

## System Environment
- **OS**: macOS (Darwin kernel with BSD userland)
- **Shell**: zsh 5.9 (interactive), bash (for scripts)
- **Package Manager**: Homebrew
- **Userland**: BSD tools, NOT GNU coreutils

## Command Verification Requirements

Before suggesting ANY destructive or system-modifying commands, AI agents MUST:

### 1. Verify macOS Compatibility
- Check command syntax against macOS man pages, not Linux documentation
- macOS uses **BSD versions** of standard Unix tools (different flags than GNU)
- Common differences:
  - `pkill` has NO `-i` (interactive) flag on macOS
  - `sed` requires `-i ''` for in-place editing (not `-i` alone)
  - `date` uses different format syntax than GNU date
  - `grep` and `find` have different extended regex support

### 2. Destructive Commands Require Extra Care
Commands that can cause data loss or system issues:
- `rm`, `rmdir` - File deletion
- `pkill`, `killall`, `kill` - Process termination
- `dd` - Disk operations
- `mv` when overwriting
- `chmod`, `chown` - Permission changes
- `sudo` anything - System-level changes
- `brew uninstall` - Package removal

**Required actions:**
1. Verify command exists on macOS: `which <command>` or `man <command>`
2. Check flag compatibility with BSD version
3. Suggest preview/dry-run mode FIRST when available
4. Warn user about the operation's impact

### 3. Process Management (pkill, kill, killall)
**Critical macOS-specific rules:**
- `pkill -i` does NOT exist on BSD (no interactive mode)
- `pkill -l <pattern>` to preview matched processes BEFORE killing
- `pkill <pattern>` sends SIGTERM (graceful) - preferred
- `pkill -9 <pattern>` sends SIGKILL (forced) - use only when needed
- Always suggest preview first: `pgrep -l <pattern>` or `pkill -l <pattern>`

**Example workflow:**
```bash
# First: Preview what will be affected
pgrep -l Mail

# Then: Graceful termination
pkill Mail

# Only if needed: Force kill
pkill -9 Mail
```

### 4. File Operations Best Practices
- For `rm`: Suggest `ls` or `find` preview first
- For `sed -i`: Always use `-i ''` on macOS (backup extension required for in-place)
- For mass operations: Show example command on test data first

### 5. When Uncertain
If you're not 100% certain about macOS compatibility:
1. State the uncertainty explicitly
2. Suggest verifying with `man <command>` first
3. Provide the command to check rather than guessing

**Example:**
> "I'm not certain if this flag works on macOS's BSD version. Let's check first:
> ```bash
> man pkill | grep -A5 OPTIONS
> ```"

## Never Assume

- ❌ DO NOT assume GNU coreutils behavior on macOS
- ❌ DO NOT suggest Linux-specific flags without verification
- ❌ DO NOT run destructive commands without user review
- ✅ DO verify against macOS documentation
- ✅ DO suggest preview/dry-run options first
- ✅ DO explain the command's behavior and risks

## Command Verification Checklist

Before suggesting a command, verify:
- [ ] Does this command exist on macOS? (`which <command>`)
- [ ] Are the flags BSD-compatible? (not GNU-specific)
- [ ] Is this destructive? (if yes, suggest preview first)
- [ ] Have I explained what this command does and its risks?
- [ ] Is there a safer alternative?

## Related Resources
- macOS man pages: `man <command>`
- Homebrew for GNU tools: `brew install coreutils` (installs g-prefixed versions)
- Check BSD vs GNU: https://unix.stackexchange.com/questions/tagged/bsd+gnu
