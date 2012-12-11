#!/bin/bash

script_dir=$(cd `dirname $1` && pwd)
script=`basename $1`
f="$script_dir/$script"
cur_dir=`pwd`
slash_cur_dir=${cur_dir//\//\\/}
exist=`grep ^$cur_dir$ $f`
declare -a bag

color=(30 31 32 33 34 35 36 37)
color_i=0
function colorful_echo()
{
    color_i=($color_i+1)%${#color[@]}
    printf "\033[49;%d;1m%s\033[m\n" ${color[$color_i]} "$1"
}

while true;do
    [ 't'$2 == 'ta' ] && [ -z $exist ] && sed -i "/^EOF$/i\\${cur_dir}" $f && break
    [ 't'$2 == 'ta' ] && [ $exist ] && echo "$cur_dir already added!" && break
    [ 't'$2 == 'td' ] && [ $exist ] && sed -i "/^${slash_cur_dir}$/d" $f && break
    [ 't'$2 == 'td' ] && [ -z $exist ] && echo "$cur_dir does NOT exist!" && break
    if [ 't'$2 != 't' ]; then
        echo "gg: go to the directory you want quickly"
        echo "Usage: gg [-a] [-d]"
        echo "Options:"
        echo "  -h        : this help"
        echo "  -a        : store current directory"
        echo "  -d        : remove current directory"
        break
    fi
    i=0
    while read d
    do
        let i=i+1
        bag[$i]=$d
        colorful_echo $i:$d
    done <<EOF
/home/zhanggl/WorkSpace
/home/zhanggl/WorkSpace/isdp
/home/zhanggl/WorkSpace/tmp
/home/zhanggl/WorkSpace/isdp/source
/home/zhanggl
/home/zhanggl/WorkSpace/apache/httpd-2.4.3
/home/zhanggl/WorkSpace/scribe
/home/imeiding/sns
/instreet/scribe/current
/home/zhanggl/WorkSpace/learn
/home/zhanggl/WorkSpace/clivia
/home/zhanggl/WorkSpace/hiredis-master
/var/log/scribe
EOF
    echo -ne "Where to go?\t"
    read p
    [ 'x'${bag[$p]} != 'x' ] && cd ${bag[$p]}
    break
done
