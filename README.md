dotfiles
========

A set of dotfiles for use on any machine, development or production. This repository organises dotfiles into package-based directories that can be symlinked to the home directory using GNU Stow.

## What's Included

This repository contains configuration packages for the following tools:

- **aws/**: AWS CLI configuration including custom aliases
- **claude/**: Claude Code configuration and custom commands  
- **ledger/**: Ledger CLI configuration
- **ruby/**: Ruby gem configuration (`.gemrc`)
- **tmux/**: Terminal multiplexer configuration
- **vim/**: Vim editor configuration

## Requirements

* (Optional) [GNU Stow](http://www.gnu.org/software/stow/) - for automatic symlinking

## Installation

### Automatic Installation with GNU Stow (Recommended)

GNU Stow automates the creation of symlinks from package directories to your home directory.

1. Clone this repository into a subdirectory of your home directory:
   ```bash
   cd ~
   git clone <repository-url> dotfiles
   cd dotfiles
   ```

2. Install all dotfiles packages:
   ```bash
   ./bootstrap-stow.sh
   ```

3. Or install specific packages:
   ```bash
   stow ruby    # Installs ~/.gemrc
   stow vim     # Installs vim configuration
   stow tmux    # Installs tmux configuration
   ```

### Useful Commands

Preview what would be installed (dry run):
```bash
stow -n <package-name>
```

Remove a package:
```bash
stow -D <package-name>
```

Reinstall a package:
```bash
stow -R <package-name>
```

### Manual Installation

For systems without Stow, manually symlink the files:

```bash
cd $HOME
ln -s dotfiles/ruby/.gemrc .gemrc
ln -s dotfiles/vim/.vimrc .vimrc
# etc.
```

## How It Works

Each package directory contains dotfiles with their expected relative path from the home directory. When you run `stow <package>`, it creates symlinks in your home directory pointing to the files in the package directory.

For example:
- `ruby/.gemrc` → `~/.gemrc`
- `vim/.vimrc` → `~/.vimrc`
- `tmux/.tmux.conf` → `~/.tmux.conf`

## Troubleshooting

**File already exists**: If Stow complains about existing files, either remove them or use `stow --adopt` to move existing files into the package.

**Permission denied**: Ensure you have write permissions to your home directory and the dotfiles repository.


