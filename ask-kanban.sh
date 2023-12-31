#!/bin/bash
#
# A simple script to download the Ask Kanban-cards by Huge.io from Medium.com
#
# last updated by P.Schweizer on 31.12.2023 14:55
#

# init vars
URL="https://blog.huge.io/ending-stale-stand-ups-with-ask-kanban-64de6c084d60"
TmpDir="/tmp/agilecards-downloads"
ImgDir="static"
Counter=0

# check and prepare directories
echo "Starting up..."
if [ ! -d "$ImgDir" ]; then echo "ERORR - directory" "$ImgDir" "does not exist here!" && exit; fi
mkdir -p "$TmpDir"
rm -f "$TmpDir"/*
cd "$TmpDir" || exit

# get image for banner
echo "Fetching banner image..."
Banner=$(wget -q -O - "$URL" | tr ',' '\n' | grep '.png' | grep 'https://' | grep 'fit:1100/1' | cut -d' ' -f2 | head -n 2 | tail -n 1)
echo "Banner -" "$Banner"
wget -q "$Banner" -O banner.png

# get images for cards
echo "Fetching card images..."
Cards=$(wget -q -O - "$URL" | tr ',' '\n' | grep '.png' | grep 'https://' | grep 'fit:1100/1' | cut -d' ' -f2 | tail -n 11 | head -n 10)
while IFS= read -r Card; do
   Counter=$((Counter+1))
   echo "Card" "$Counter" "-" "$Card"
   wget -q "$Card" -O askkanban"$Counter".png
done <<< "$Cards"

# make backup of img directory when not empty
cd - > /dev/null || exit
if [ -n "$(ls -A "$ImgDir")" ]; then
   Timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
   echo "Backup $ImgDir to $ImgDir-$Timestamp"
   cp -rp "$ImgDir" "$ImgDir"-"$Timestamp"
fi

# copy files from tmp directory to img directory
echo "Copy files..."
cp -rp "$TmpDir"/* "$ImgDir"/

# remove temp. stuff
echo "Cleaning up..."
rm -f "$TmpDir"/*
rmdir "$TmpDir"
echo "Done."
