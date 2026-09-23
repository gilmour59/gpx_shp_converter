#!/bin/bash
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# GitHub/browser downloads are quarantined by macOS. Because this release is
# not yet Apple Developer-ID notarized, Gatekeeper may otherwise block nested
# bundled frameworks such as Python.framework as "damaged".
xattr -dr com.apple.quarantine "$SCRIPT_DIR" 2>/dev/null || true

chmod +x "./GPX_SHP_Converter"

exec "./GPX_SHP_Converter"
