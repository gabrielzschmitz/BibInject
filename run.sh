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

# Virtual environment and CLI module
VENV_NAME=".venv"
APP_MODULE="src.app"

# --- Debug Mode (via global environment variable) ---
# Usage: DEBUG=TRUE ./run.sh ...
if [[ "$DEBUG" == "TRUE" || "$DEBUG" == "true" || "$DEBUG" == "1" ]]; then
  DEBUG_MODE=true
else
  DEBUG_MODE=false
fi

# Helper for conditional info messages
log_info() {
  if $DEBUG_MODE; then
    echo -e "${INFO} $1"
  fi
}

# --- Virtual environment check ---
if [ ! -d "$VENV_NAME" ]; then
  echo -e "${RED}${ERROR} Virtual environment '${VENV_NAME}' not found.${RESET}"
  exit 1
fi

log_info "Activating virtual environment '${VENV_NAME}'..."
source "$VENV_NAME/bin/activate"

# --- Argument check ---
if [ $# -eq 0 ]; then
  echo -e "${YELLOW}${INFO} No arguments supplied.${RESET}"
  echo "Example usage:"
  echo "  ./run.sh --input refs.bib --refspec templates/apa.html --template index.html --target-id references output.html"
  deactivate
  exit 1
fi

# --- Run Python CLI ---
log_info "Running ${YELLOW}${APP_MODULE}${RESET} with arguments: $*"
python -m "$APP_MODULE" "$@"

# --- Cleanup ---
log_info "Deactivating the virtual environment... ${CHECKMARK}"
deactivate

echo -e "${GREEN}${CHECKMARK} Done.${RESET}"
