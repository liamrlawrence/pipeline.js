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
    -p 7655:8501 \
    -p 7656:8007 \
    -v $(pwd)/cmd:/app/cmd:ro,cached \
    -v $(pwd)/internal:/app/internal:rw,cached \
    -v $(pwd)/static:/app/static:rw,cached \
    -v $(pwd)/scripts:/app/scripts:rw,cached \
    -v $(pwd)/node_modules:/node_modules_cache:rw,cached \
    --network nginx-net \
    --ip 172.30.0.123 \
    --name $CONTAINER_NAME \
    $IMAGE_NAME

