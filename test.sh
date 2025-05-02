#!/bin/bash

set -e

# Docker compose project name
PROJECT_NAME="cgn-ec-consumer-tests"

# Compose command, override if needed
doco="docker compose --file ./docker-compose.test.yml --project-name ${PROJECT_NAME}"

start_services() {
  echo "🏗 Starting services..."
  $doco up --detach --quiet-pull --wait
}

run_tests() {
  echo "🚀 Running tests..."
  # For example, run pytest inside API container
  $doco run --rm api pytest tests/
  # Optionally, if you also want to run consumer tests separately:
  $doco run --rm consumer pytest tests/
}

cleanup() {
  echo "💣 Cleaning up..."
  $doco logs --no-color || true
  $doco down --volumes
}

trap cleanup EXIT ERR

echo "🐳 Start integration testing"

start_services
run_tests

echo "✅ Integration tests passed"