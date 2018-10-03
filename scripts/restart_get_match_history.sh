#!/bin/bash

REGION="$1"
CURRENT_DIR=`echo $(cd $(dirname $0) && pwd)`
BASE_DIR="$CURRENT_DIR/.."

if [ -e $BASE_DIR/3v3_$REGION.pid ]; then
    cat $BASE_DIR/3v3_$REGION.pid & kill $!
fi
if [ -e $BASE_DIR/5v5_$REGION.pid ]; then
    cat $BASE_DIR/5v5_$REGION.pid & kill $!
fi

nohup python $BASE_DIR/get_match_history.py ranked $REGION >> $BASE_DIR/log/get_match_history_3v3_$REGION.log & echo $! > $BASE_DIR/3v3_$REGION.pid
nohup python $BASE_DIR/get_match_history.py ranked5v5 $REGION >> $BASE_DIR/log/get_match_history_5v5_$REGION.log & echo $! > $BASE_DIR/5v5_$REGION.pid