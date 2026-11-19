#!/bin/sh
cd "$(dirname "$0")" || exit 1
if command -v node >/dev/null 2>&1; then
  node server.mjs --open
elif command -v python3 >/dev/null 2>&1; then
  python3 server.py --open
else
  printf '%s\n' 'Please install Node.js 20 or later: https://nodejs.org/'
fi
