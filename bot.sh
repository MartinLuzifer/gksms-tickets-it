#!/usr/bin/bash

export red='\033[0;31m'
export green='\033[1;36m'
export nc='\033[0m'
export tgb_image_name='tgb-gksms-dev-tickets-it'
export tgb_container_name='tgb'
export args_not_found="
${red}ARGS NOT FOUND.${nc}

${green}USED:${nc}
${green}START${nc} BOT----> ./bot.sh ${green}start${nc}
${green}STOP${nc} BOT -----> ./bot.sh ${green}stop${nc}
GET ${green}HELP${nc} -----> ./bot.sh ${green}help${nc}

${red}
!!! NOT RUN sh bot.sh start
!!! NOT RUN bash bot.sh start.
!!! ONLY ./bot.sh
${nc}
"

if [ "$1" == 'start' ]; then

  echo "$1" && \
  sudo docker build -t $tgb_image_name . && \
  sudo docker run -d --name $tgb_container_name $tgb_image_name

elif [ "$1" == 'stop' ]; then

  echo "$1" && \
  sudo docker container stop $tgb_container_name && \
  sudo docker container rm $tgb_container_name && \
  sudo docker image rm $tgb_image_name

elif [ -n "$1" -o ! "$1" ]; then
  echo -e "$args_not_found"

elif [ "$1" == "help" ]; then
  echo -e "$args_not_found"

fi
