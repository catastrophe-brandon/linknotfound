#!/bin/bash

if [ "$#" -eq  "1" ]
  then
    LNF_CMD="$1"
else
  LNF_CMD="--help"
fi

docker run -e LINKNOTFOUND_RUN="$LNF_CMD" -it linknotfound /bin/bash
