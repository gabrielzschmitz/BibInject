#!/bin/bash

# Define Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'

# Define Emojis
CHECKMARK="✅"
ERROR="❌"
INFO="ℹ️"

# Assign the virtual environment name and app
VENV_NAME=".venv"
APP_FILE="src.app"

# Check if the virtual environment exists
if [ ! -d "$VENV_NAME" ]; then
  echo -e "${RED}${ERROR} Virtual environment '${VENV_NAME}' not found.${RESET}"
  exit 1
fi

# Activate the virtual environment
echo -e "${INFO} Activating virtual environment '${VENV_NAME}'..."
source "$VENV_NAME/bin/activate"

# Run the app.py script
echo -e "${INFO} Running ${YELLOW}app.py${RESET}..."
python -m "$APP_FILE"

# Deactivate the virtual environment
echo -e "${INFO} Deactivating the virtual environment... ${CHECKMARK}"
deactivate

echo -e "${GREEN}${CHECKMARK} Virtual environment deactivated.${RESET}"
