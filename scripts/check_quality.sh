#!/bin/bash
set -e

echo "Running Ruff Format Check..."
ruff format --check .

echo "Running Ruff Lint Check..."
ruff check .

echo "Running Mypy Type Check..."
mypy .
