#!/bin/bash
# 프레임(JPG) + 나레이션 WAV → MP4, 이어 붙인 전체 영상 full.mp4
set -e
OUT=${OUT:-out}; mkdir -p $OUT
for n in 0 1 2 3 4 5 6; do
  ffmpeg -y -loglevel error -framerate 20 -i /tmp/frames/$n/%05d.jpg -i /tmp/audio/ep$n.wav \
    -vf "fps=30,format=yuv420p" -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 160k -ar 44100 -ac 2 -shortest -movflags +faststart $OUT/ep$n.mp4
done
cd $OUT; rm -f list.txt; for n in 0 1 2 3 4 5 6; do echo "file 'ep$n.mp4'" >> list.txt; done
ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -c copy -movflags +faststart full.mp4; rm list.txt
ls -la
