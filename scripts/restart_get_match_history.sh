#!/bin/bash

GAMEMODE="$1"
REGION="$2"
CURRENT_DIR=`echo $(cd $(dirname $0) && pwd)`
BASE_DIR="$CURRENT_DIR/.."

if test $GAMEMODE = "ranked"; then
    if [ -e $BASE_DIR/3v3_ranked_${REGION}.pid ]; then
        PID=`cat $BASE_DIR/3v3_ranked_${REGION}.pid`
        rm -f $BASE_DIR/3v3_ranked_${REGION}.pid
        kill $PID
    fi
    if [ -e $BASE_DIR/5v5_ranked_${REGION}.pid ]; then
        PID=`cat $BASE_DIR/5v5_ranked_${REGION}.pid`
        rm -f $BASE_DIR/5v5_ranked_${REGION}.pid
        kill $PID
    fi
    nohup python $BASE_DIR/get_match_history.py ranked $REGION >> $BASE_DIR/log/get_match_history_3v3_${GAMEMODE}_${REGION}.log & echo $! > $BASE_DIR/3v3_${GAMEMODE}_${REGION}.pid
    nohup python $BASE_DIR/get_match_history.py ranked5v5 $REGION >> $BASE_DIR/log/get_match_history_5v5_${GAMEMODE}_${REGION}.log & echo $! > $BASE_DIR/5v5_${GAMEMODE}_${REGION}.pid
fi
if test $GAMEMODE = "private5v5"; then
    if [ -e $BASE_DIR/5v5_private_${REGION}.pid ]; then
        PID=`cat $BASE_DIR/5v5_private_${REGION}.pid`
        rm -f $BASE_DIR/5v5_private_${REGION}.pid
        kill $PID
    fi
    if [ -e $BASE_DIR/5v5_private_draft_${REGION}.pid ]; then
        PID=`cat $BASE_DIR/5v5_private_draft_${REGION}.pid`
        rm -f $BASE_DIR/5v5_private_draft_${REGION}.pid
        kill $PID
    fi
    nohup python $BASE_DIR/get_match_history.py private5v5 $REGION >> $BASE_DIR/log/get_match_history_5v5_private_${REGION}.log & echo $! > $BASE_DIR/5v_5private_${REGION}.pid
    nohup python $BASE_DIR/get_match_history.py private_draft5v5 $REGION >> $BASE_DIR/log/get_match_history_5v5_private_draft_${REGION}.log & echo $! > $BASE_DIR/5v5_private_draft_${REGION}.pid
fi
if test $GAMEMODE = "casual"; then
    if [ -e $BASE_DIR/3v3_ranked_${REGION}.pid ]; then
        PID=`cat $BASE_DIR/3v3_casual_${REGION}.pid`
        rm -f $BASE_DIR/3v3_casual_${REGION}.pid
        kill $PID
    fi
    if [ -e $BASE_DIR/5v5_casual_${REGION}.pid ]; then
        PID=`cat $BASE_DIR/5v5_casual_${REGION}.pid`
        rm -f $BASE_DIR/5v5_casual_${REGION}.pid
        kill $PID
    fi
    nohup python $BASE_DIR/get_match_history.py casual $REGION >> $BASE_DIR/log/get_match_history_3v3_${GAMEMODE}_${REGION}.log & echo $! > $BASE_DIR/3v3_${GAMEMODE}_${REGION}.pid
    nohup python $BASE_DIR/get_match_history.py casual5v5 $REGION >> $BASE_DIR/log/get_match_history_5v5_${GAMEMODE}_${REGION}.log & echo $! > $BASE_DIR/5v5_${GAMEMODE}_${REGION}.pid
fi