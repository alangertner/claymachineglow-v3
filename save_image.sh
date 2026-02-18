#!/bin/bash
# Usage: save_image.sh <base64_string> <output_path>
echo "$1" | base64 -d > "$2"
