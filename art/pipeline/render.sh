#!/bin/sh
# Render + pixelize one creature:  sh art/pipeline/render.sh rat
# (Jay never needs to run this; Claude does.)
set -e
cd "$(dirname "$0")/../.."
BLENDER="${BLENDER:-/c/Program Files/Blender Foundation/Blender 5.3/blender.exe}"
"$BLENDER" -b --factory-startup --python art/pipeline/render_creature.py -- "$@" 2>&1 | grep -E "rendered|Error|Traceback|File \"" || true
python art/pipeline/pixelize.py "$1"
