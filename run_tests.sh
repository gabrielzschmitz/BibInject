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
TEST="🧪"

# Settings
VENV_NAME=".venv"
TEST_DIR="src/tests"
VERBOSE_FLAG=""
TARGET_PATH="$TEST_DIR"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -v|--verbose)
      VERBOSE_FLAG="--log-cli-level=DEBUG"
      shift
      ;;
    *)
      TARGET_PATH="$1"
      shift
      ;;
  esac
done

# Check if the virtual environment exists
if [ ! -d "$VENV_NAME" ]; then
  echo -e "${RED}${ERROR} Virtual environment '${VENV_NAME}' not found.${RESET}"
  exit 1
fi

# Activate virtual environment
echo -e "${INFO} Activating virtual environment '${VENV_NAME}'..."
source "$VENV_NAME/bin/activate"

# Run pytest with PYTHONPATH set
echo -e "${TEST} Running tests in ${YELLOW}${TARGET_PATH}${RESET}..."
PYTHONPATH=$(pwd) pytest -v $VERBOSE_FLAG "$TARGET_PATH"

# Check exit status
if [ $? -eq 0 ]; then
  echo -e "${GREEN}${CHECKMARK} All tests passed successfully.${RESET}"
else
  echo -e "${RED}${ERROR} Some tests failed.${RESET}"
fi

# Deactivate virtual environment
echo -e "${INFO} Deactivating virtual environment... ${CHECKMARK}"
deactivate
