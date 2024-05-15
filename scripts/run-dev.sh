#!/bin/bash
# run-dev.sh


PROJECT_NAME="nodejs"
IMAGE_NAME="${PROJECT_NAME}_image"
CONTAINER_NAME="${PROJECT_NAME}_container"



sudo docker build \
    -f ./deployments/Dockerfile \
    --target dev \
    -t $IMAGE_NAME \
    .


sudo docker run \
    --rm \
    -it \
    -e "TERM=xterm-256color" \
    -p 7654:8080 \
    -v ./cmd:/app/cmd:ro,cached \
    -v ./internal:/app/internal:rw,cached \
    -v ./static:/app/static:rw,cached \
    -v ./node_modules:/app/node_modules:rw,cached \
    --network nginx-net \
    --ip 172.30.0.123 \
    --name $CONTAINER_NAME \
    $IMAGE_NAME

