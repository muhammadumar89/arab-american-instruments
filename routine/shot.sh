#!/bin/sh
# Screenshots for the look and feel track without the preview pane (headless Chrome).
#   sh routine/shot.sh desktop <out.png> <url>            1440 x 900
#   sh routine/shot.sh phone   <out.png> <url> [height]   true 375 wide viewport
# Headless Chrome will not lay out narrower than 500px, so the phone shot loads the page in a 375px iframe
# and crops. For a local after shot: AAI_BASE="file://$PWD/site" python3 build.py, shoot file://$PWD/site/index.html,
# then rebuild with AAI_BASE unset before the push.
C="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; T=$(mktemp -d)
if [ "$1" = phone ]; then H=${4:-812}
  printf '<!doctype html><body style="margin:0;background:#000"><iframe src="%s" style="border:0;width:375px;height:%spx;display:block"></iframe>' "$3" "$H" > "$T/wrap.html"
  "$C" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$T/chr" --virtual-time-budget=7000 --window-size=600,$H --screenshot="$2" "file://$T/wrap.html" >/dev/null 2>&1
  python3 -c "import sys; from PIL import Image; im=Image.open(sys.argv[1]); im.crop((0,0,375,im.size[1])).save(sys.argv[1])" "$2"
else
  "$C" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$T/chr" --virtual-time-budget=6000 --window-size=1440,900 --screenshot="$2" "$3" >/dev/null 2>&1
fi
rm -rf "$T"; ls -la "$2"
