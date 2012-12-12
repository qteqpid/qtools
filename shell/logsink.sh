#!/bin/bash
# script for fetching logs from remote server
# Usage: sh logsink.sh 1      or
#        sh logsink.sh 20121102/02
# Author: qteqpid@163.com
# 
function usage()
{
	echo "Usage: sh ./logsink.sh [num hours ago|date]"
	echo "    Example: sh ./logsink.sh 1"
	echo "             sh ./logsink.sh 20121101/02"
	exit 1
}

if [[ $# -ne 1 ]];then
	usage
else
	expr $1 "+" 10 &> /dev/null
	if [[ $? -ne 0 ]];then # 20121101/02
		echo $1 | grep -E "^[0-9]{8}/[0-9]{2}$" &> /dev/null
		if [[ $? -ne 0 ]];then
			usage
		else
			curtime=$1
		fi
	else                   # 1
		curtime=$(date -d "$1 hour ago" +"%Y%m%d/%H")
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

grep $curtime done &> /dev/null
if [[ $? -eq 0 ]];then
	echo $curtime" already fetched!"
	exit
fi

cd `dirname $0`
mkdir -p $curtime
rv=0
download $curtime 210.xxx.xxx.xxx username password /home/instreet/isdp/locallogs ; rv=$((rv+$?))
download $curtime 210.xxx.xxx.xxx username password /instreet/isdp/locallogs ; rv=$((rv+$?))

if [[ $rv -eq 0 ]];then
	echo "Download $curtime successful!"
	echo $curtime >> done	
else
	echo "Download $curtime failed!"
	rm -rf $curtime
fi
