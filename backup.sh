#!/bin/sh
export DATE=`date "+20%y%m%d"`
cd /home/tmax-ai
tar -zcvf /home/tmax-ai/backup/ai-app$DATE.tar.gz  ./ai-app
find /home/tmax-ai/backup -mtime 30 -exec rm {} \;