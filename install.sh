#!/bin/bash

# Define Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Define Emojis
CHECKMARK="✅"
ERROR="❌"
INFO="ℹ️"

# Assign the virtual environment name
VENV_NAME="src/.venv"

# Create a virtual environment
echo -e "${INFO} Creating virtual environment '${BLUE}$VENV_NAME${RESET}'..."
python -m venv "$VENV_NAME"

# Activate the virtual environment
source "$VENV_NAME/bin/activate"

# Install dependencies
echo -e "${INFO} Installing dependencies... ${YELLOW}Please wait.${RESET}\n"
pip install -r requirements.txt

# Verify installation
echo -e "\n${INFO} Installation complete. ${GREEN}${CHECKMARK}${RESET}"
pip list

# Final Message
echo -e "\n${GREEN}${CHECKMARK} Virtual environment '${BLUE}$VENV_NAME${RESET}' created and dependencies installed!${RESET}"
