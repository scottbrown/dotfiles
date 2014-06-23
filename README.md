dotfiles
========

A set of dotfiles for use on any machine, development or production.

## Requirements

* (Optional) [GNU Stow](http://www.gnu.org/software/stow/)

## Automatic Installation with GNU Stow

If using this method, GNU Stow is a mandatory requirement.

This repository should be cloned into a subdirectory of the user's home directory.  For instance:

    ~/dotfiles

If this is done, then to install each of the dotfiles automatically, perform the following:

    $ ./bootstrap-stow.sh

If only a specific dotfile (for instance, ``.gemrc``) is needed, it can still be installed through Stow with the following:

    $ stow ruby

## Manual Installation

For those systems without Stow, each dotfile can be installed by copying or symlinking to the dotfile in the package directory.  For instance, to install the ``.gemrc`` file:

    $ cd $HOME
    $ ln -s dotfiles/ruby/.gemrc .gemrc

If manual installation is preferred, then this repository can be clone into any directory on the machine.


