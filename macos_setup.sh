#!/bin/bash

readonly SHELL_NAME="zsh"
readonly INSTALL_TEX=1 # For matplotlib visualizations.

if (( $INSTALL_TEX )); then
    brew install texlive
fi
brew install --cask anaconda
conda create --name tppfaas python=3.9
conda init $SHELL_NAME
exec $SHELL_NAME
conda activate tppfaas
pip install -r requirements.txt