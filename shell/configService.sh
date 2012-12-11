#!/bin/bash
# 配置centos服务器的服务，支持开启、关闭、显示、自动配置服务
# Author: Qteqpid
# Date: Thu Sep 20 11:06:46 CST 2012

# 推荐开启的服务
recommendServices=(
    anacron
    autofs
    cpuspeed
    crond
    gpm
    irqbalance
    iscsi
    iscsid
    kudzu
    lvm2-monitor
    mysql
    netfs
    network
    nfslock
    portmap
    rawdevices
    readahead_early
    readahead_later
    smartd
    sshd
    syslog
    xinetd
)

while true
do
    read -p ">" service
    case $service in
        help)
            echo "指令说明:"
            echo -e "\thelp         显示该帮助"
            echo -e "\ton           显示所有开启的服务"
            echo -e "\toff          显示所有关闭的服务"
            echo -e "\tservicename  启停指定的服务"
            echo -e "\tauto         根据建议自动配置服务"
            echo -e "\texit         退出"
            continue
            ;;
        exit)
            exit 0
            ;;
        on)
            chkconfig --list | grep ":on"
            continue
            ;;
        off)
            chkconfig --list | grep ":off"
            continue
            ;;
        auto)
            opened=$(chkconfig --list | grep ":on" | awk '{print $1}')
            # 关掉不在推荐列表里的服务
            for i in $opened
            do
                echo "${recommendServices[*]}" | grep "$i" &> /dev/null
                if [ $? -ne 0 ];then
                    chkconfig $i off
                    service $i stop
                    echo "close $i"
                fi
            done
            # 开启推荐列表里的服务
            for i in ${recommendServices[*]}
            do
                echo "$opened" | grep "$i"  &> /dev/null
                if [ $? -ne 0 ];then
                    chkconfig $i on
                    service $i start
                    echo "open $i"
                fi
            done
            continue
            ;;
        *)
            ;;
    esac
            
    chkconfig --list $service 2> /dev/null
    if [ $? -ne 0 ];then
        echo "No such service $service!"
    else
        read -p "close or open?[C/o]" action
        if [ "x"$action == "xo" ];then
            chkconfig $service on
            service $service start
            echo "$service opened!"
        else
            chkconfig $service off
            service $service stop
            echo "$service closed!"
        fi
    fi
done
