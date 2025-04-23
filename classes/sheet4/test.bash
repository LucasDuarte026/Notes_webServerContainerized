#!/bin/bash

get_username_id(){
    if [[ $# -ne 1 ]]; then
        echo error
        exit
    fi
    cat /proc/$1/status | grep "Uid" | grep -oP '[0-9]+' | head -n 1
}

get_user(){

    if [[ $# -ne 1 ]]; then
        echo error
        exit
    fi
    id -un $1 
}


get_cmdline(){
    if [[   $# -ne 1 ]]; then
        echo erros
        exit
    fi
    cat /proc/$1/cmdline | tr '\0 ' '\n\n' | head -1
}
echo charles teste
echo -e "pid\t\tuid\t\tuname\t\tcmdline"
echo -e "===\t\t===\t\t=====\t\t======"

for process_PID in $(ls /proc | grep -oP '[0-9]+' | sort -n); do
    user_id=$(get_username_id $process_PID)
    user_name=$(get_user $user_id)
    CMD_LINE=$(get_cmdline $process_PID)
    echo -e "$process_PID\t\t$user_id\t\t$user_name\t\t$CMD_LINE"
    # echo -e "$user_id\t$process_PID\t$process_UID"
done
