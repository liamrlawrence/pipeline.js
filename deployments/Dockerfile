FROM golang:1.22-bookworm AS base
WORKDIR /app

RUN go install github.com/a-h/templ/cmd/templ@v0.2.663

COPY go.mod go.sum ./
RUN go mod download && go mod verify



WORKDIR /app
LABEL description="Golang dev web server"
ENV ENVIRONMENT "DEV"
ENV TERM xterm-256color

RUN apt-get update &&\
    apt-get install -y --no-install-recommends vim \
    nodejs npm


COPY configs/package.json configs/tsconfig.json configs/tsup.config.ts ./
RUN npm install

RUN go install github.com/liamrlawrence/observer/cmd/observer@74dd289
COPY configs/observer.config.json .
COPY Makefile .

VOLUME [                    \
    "/app/cmd"              \
    "/app/internal"         \
    "/app/static"           \
    "/node_modules_cache"   \
]
EXPOSE 8080
CMD ["observer", "-debug=true"]

