#!/bin/bash
# script for fetching logs from remote server
# Usage: sh logsink.sh 1
# Author: zhanggl@instreet.cn
# 

function usage()
{
    echo "Usage: sh ./logsink.sh [number]"
    exit 1
}

if [[ $# -ne 1 ]];then
    usage
else
    expr $1 "+" 10 &> /dev/null
    if [[ $? -ne 0 ]];then
        echo "Error: argument must be a number"
        usage
    fi
fi

function download()
{
ftp -in <<EOF
open $2
user $3 $4
bin
cd $5
passive
mget $1
bye
EOF
    return 0
}

curtime=$(date -d "$1 hour ago" +"%Y%m%d/%H")
grep $curtime done &> /dev/null
if [[ $? -eq 0 ]];then
    echo $curtime" already fetched!"
    exit
fi

cd `dirname $0`
mkdir -p $curtime
rv=0
download $curtime remoteserver username password /home/instreet/isdp/locallogs ; rv=$((rv+$?))
download $curtime remoteserver username password /instreet/isdp/locallogs ; rv=$((rv+$?))

if [[ $rv -eq 0 ]];then
    echo "Download $curtime successful!"
    echo $curtime >> done
else
    echo "Download $curtime failed!"
    rm -rf $curtime
fi
