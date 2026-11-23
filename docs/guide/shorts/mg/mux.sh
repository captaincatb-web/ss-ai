#!/bin/bash
# 프레임 + 나레이션 → out/ep0~6.mp4, 이어 붙인 out/full.mp4
set -e; cd "$(dirname "$0")"; mkdir -p out
for n in 0 1 2 3 4 5 6; do
  ffmpeg -y -loglevel error -framerate 30 -i /tmp/mg_frames/$n/%05d.jpg -i /tmp/mg_audio/ep$n.wav -c:v libx264 -preset medium -crf 24 -pix_fmt yuv420p -c:a aac -b:a 160k -ar 44100 -ac 2 -shortest -movflags +faststart out/ep$n.mp4
done
cd out; printf "file 'ep%s.mp4'\n" 0 1 2 3 4 5 6 > list.txt; ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -c copy -movflags +faststart full.mp4; rm list.txt; ls -la
