#!/bin/sh
# Render + pixelize one creature:  sh art/pipeline/render.sh rat
# (Jay never needs to run this; Claude does.)
set -e
cd "$(dirname "$0")/../.."
# Approved sprites are frozen (art/APPROVED.txt). FORCE=1 overrides, only when Jay asks for a change.
if [ -z "$FORCE" ] && grep -qx "$1" art/APPROVED.txt 2>/dev/null; then
  echo "REFUSED: '$1' is approved by Jay and frozen (art/APPROVED.txt). Use FORCE=1 only if Jay asked for a change."
  exit 1
fi
BLENDER="${BLENDER:-/c/Program Files/Blender Foundation/Blender 5.3/blender.exe}"
"$BLENDER" -b --factory-startup --python art/pipeline/render_creature.py -- "$@" 2>&1 | grep -E "rendered|Error|Traceback|File \"" || true
python art/pipeline/pixelize.py "$1"
