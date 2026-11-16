#!/bin/sh
# Fonts are not committed (ads_meta/fonts is gitignored). Re-download them from the npm registry.
set -e
T=$(mktemp -d); cd "$T"
npm pack pretendard @fontsource/black-han-sans @fontsource/nanum-pen-script >/dev/null
D=/home/user/123/ads_meta/fonts; mkdir -p "$D/bhs" "$D/pen"
for t in *.tgz; do mkdir -p "x_$t"; tar xzf "$t" -C "x_$t"; done
cp x_pretendard-*/package/dist/public/variable/PretendardVariable.ttf "$D/"
cp -r x_fontsource-black-han-sans-*/package/files x_fontsource-black-han-sans-*/package/400.css "$D/bhs/"
cp -r x_fontsource-nanum-pen-script-*/package/files x_fontsource-nanum-pen-script-*/package/400.css "$D/pen/"
echo fonts ready in "$D"
