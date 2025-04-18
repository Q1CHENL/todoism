#!/bin/bash

# Step 1: Generate test data
python3 test/generate.py || { echo "Failed to generate test data"; exit 1; }

# Step 2: Run the container with mounts and start todoism
docker run --rm -it \
  -e HOME=/home/user \
  -e TERM=xterm-256color \
  -w /workspace \
  -v "$PWD":/workspace:Z \
  ubuntu-todoism \
  python3 -m todoism --dev "$@"
