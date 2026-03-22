#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies using Poetry
pip install --upgrade pip
pip install poetry

# Configure poetry to not create a virtual environment (Render already provides one)
poetry config virtualenvs.create false

# Install dependencies
poetry install --no-dev --no-interaction --no-ansi
