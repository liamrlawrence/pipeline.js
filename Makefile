.PHONY: all go ts

all: go templ ts

go: templ
	@echo "Building Go project..."
	go build -v -o ./tmp/main ./cmd/server

templ:
	@echo "Building Templ files..."
	go generate ./internal/pages/generate.go

ts:
	@echo "Building TypeScript project..."
	npm run build

