FROM golang:1.22-bookworm AS base
WORKDIR /app

RUN go install github.com/a-h/templ/cmd/templ@v0.2.663

COPY go.mod go.sum ./
RUN go mod download && go mod verify



FROM base AS dev
WORKDIR /app
LABEL description="Golang dev web server"
ENV ENVIRONMENT "DEV"
ENV TERM xterm-256color

RUN apt-get update &&\
    apt-get install -y --no-install-recommends vim \
    nodejs npm \
    python3 python3-dev python3-pip python3-venv python-is-python3

COPY configs/package.json configs/tsconfig.json configs/tsup.config.ts ./
RUN npm install

RUN python -m venv venv &&\
    . /app/venv/bin/activate &&\
    python -m pip install opencv-python-headless streamlit numpy fastapi uvicorn
RUN echo ". /app/venv/bin/activate" >> ~/.bashrc

RUN go install github.com/liamrlawrence/observer/cmd/observer@ff0d7bd
COPY configs/observer.config.json .
COPY Makefile .

COPY configs/streamlit .streamlit


VOLUME [                    \
    "/app/cmd"              \
    "/app/internal"         \
    "/app/static"           \
    "/app/scripts"          \
    "/node_modules_cache"   \
]
EXPOSE 8080
CMD ["/bin/bash", "-c", "source venv/bin/activate && observer -debug=true"]

