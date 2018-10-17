#!/bin/bash

GAMEMODE="$1"
REGION="$2"
CURRENT_DIR=`echo $(cd $(dirname $0) && pwd)`
BASE_DIR="$CURRENT_DIR/.."

if [ -e $BASE_DIR/3v3_$REGION.pid ]; then
    kill `cat $BASE_DIR/3v3_${GAMEMODE}_${REGION}.pid`
    rm -f $BASE_DIR/3v3_${GAMEMODE}_${REGION}.pid
fi
if [ -e $BASE_DIR/5v5_$REGION.pid ]; then
    kill `cat $BASE_DIR/5v5_${GAMEMODE}_${REGION}.pid`
    rm -f $BASE_DIR/5v5_${GAMEMODE}_${REGION}pid
fi

if test $GAMEMODE = "ranked"; then
    nohup python $BASE_DIR/get_match_history.py ranked $REGION >> $BASE_DIR/log/get_match_history_3v3_${GAMEMODE}_${REGION}.log & echo $! > $BASE_DIR/3v3_${GAMEMODE}_${REGION}.pid
    nohup python $BASE_DIR/get_match_history.py ranked5v5 $REGION >> $BASE_DIR/log/get_match_history_5v5_${GAMEMODE}_${REGION}.log & echo $! > $BASE_DIR/5v5_${GAMEMODE}_${REGION}.pid
fi
if test $GAMEMODE = "casual"; then
    nohup python $BASE_DIR/get_match_history.py casual $REGION >> $BASE_DIR/log/get_match_history_3v3_${GAMEMODE}_${REGION}.log & echo $! > $BASE_DIR/3v3_${GAMEMODE}_${REGION}.pid
    nohup python $BASE_DIR/get_match_history.py casual5v5 $REGION >> $BASE_DIR/log/get_match_history_5v5_${GAMEMODE}_${REGION}.log & echo $! > $BASE_DIR/5v5_${GAMEMODE}_${REGION}.pid
fi