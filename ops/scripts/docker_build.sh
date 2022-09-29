#!/bin/bash

docker images -q linknotfound:latest
if [ $? -eq 0 ]; then
  docker rmi linknotfound --force
fi

docker build --build-arg linknotfound_RUN="--test" -t linknotfound -f Dockerfile . --network host
echo

echo "--- images built ---"
docker image ls | grep -e 'linknotfound'
