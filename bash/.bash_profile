#!/bin/bash

# 20200823: Stop MacOS warning me about zsh being default
export BASH_SILENCE_DEPRECATION_WARNING=1

# simple per-user bash profile configuration
# https://typicalrunt.me/2014/11/06/simple-per-user-bash-configuration/
BASH_PROFILE_CONF_DIR="$HOME/.bash_profile.d"

if [[ ! -d "$BASH_PROFILE_CONF_DIR" ]]; then
  # create the configuration directory
  mkdir $BASH_PROFILE_CONF_DIR
  chmod 700 $BASH_PROFILE_CONF_DIR
fi

for profile_file in $(ls $BASH_PROFILE_CONF_DIR/*.bash); do
  source $profile_file
done
# /simple per-user bash profile configuration
