#!/bin/sh
#
# Bootstrap file to setup home directory using GNU Stow.
#
# Make sure that the dotfiles repository is in the user's home directory.
#

stow ruby
stow tmux
stow vim
stow claude

