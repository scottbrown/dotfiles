# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a personal dotfiles repository that manages configuration files for various tools using GNU Stow. The repository organises dotfiles into package-based directories that can be symlinked to the home directory automatically.

## Architecture

- **Package Structure**: Each tool's configuration is stored in its own directory (e.g., `vim/`, `tmux/`, `ruby/`, etc.)
- **Stow Integration**: Uses GNU Stow to create symlinks from package directories to the home directory
- **Bootstrap Script**: `bootstrap-stow.sh` automates the installation of all dotfiles packages

## Key Components

- `bootstrap-stow.sh`: Main installation script that runs `stow` for each package
- `aws/`: AWS CLI configuration including custom aliases
- `claude/`: Claude Code configuration and custom commands
- `ledger/`: Ledger CLI configuration
- `ruby/`: Ruby gem configuration
- `tmux/`: Terminal multiplexer configuration  
- `vim/`: Vim editor configuration

## Common Commands

**Install all dotfiles:**
```bash
./bootstrap-stow.sh
```

**Install a specific package:**
```bash
stow <package-name>
# Examples:
stow vim
stow tmux
stow claude
```

**Remove a package:**
```bash
stow -D <package-name>
```

**Preview what would be installed:**
```bash
stow -n <package-name>
```

## Development Guidelines

- New dotfiles should be organised into logical packages under their own directories
- Each package directory should contain the dotfiles with their expected relative path from the home directory
- Update `bootstrap-stow.sh` when adding new packages that should be installed by default
- Test installation with `stow -n` before committing changes
- Follow the existing Git commit conventions (present tense: "Adding vim configuration")

## File Structure Conventions

When adding new dotfiles:
- Create a package directory: `mkdir new-tool/`
- Place dotfiles with correct relative paths: `new-tool/.config/new-tool/config.yml`
- Add to bootstrap script if it should be installed by default