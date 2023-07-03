#!/usr/bin/bash

export tgb_image_name="tgb-gksms-dev-tickets-it"
export tgb_container_name='tgb'
export args_not_found="ARGS NOT FOUND, USED:
                START BOT ----> sh bot.sh start
                STOP BOT -----> sh bot.sh stop
                GET HELP -----> sh bot.sh help"

if [ "$1" == 'start' ]; then

  echo "$1"
  sudo docker build -t $tgb_image_name . && sudo docker run -d --name $tgb_container_name $tgb_image_name

elif [ "$1" == 'stop' ]; then

  echo "$1"
  sudo docker container stop $tgb_container_name && sudo docker container rm $tgb_container_name && sudo docker image rm $tgb_image_name

elif [ -n "$1" -o ! "$1" ]; then
  echo "$args_not_found"

elif [ "$1" == "help" ]; then
  echo "$args_not_found"

fi
