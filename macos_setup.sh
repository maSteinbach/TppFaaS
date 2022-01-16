#!/bin/bash

SHELL_NAME="zsh"

brew install --cask mactex-no-gui
brew install --cask anaconda
conda create --name tppfaas python=3.9
conda init $SHELL_NAME
exec zsh
conda activate tppfaas
pip install -r requirements.txt