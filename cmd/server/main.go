package main

import (
	"fmt"
	"net/http"
	"os"

	"github.com/go-chi/chi/v5"

	"github.com/liamrlawrence/nodejs/site/internal/routes"
	"github.com/liamrlawrence/nodejs/site/internal/server"
)

func initialize(s *server.Server) error {
	// Routes
	routes.SetupRouter(s)

	return nil
}

func run(s *server.Server) error {
	var ip string
	if os.Getenv("ENVIRONMENT") == "PRODUCTION" {
		ip = ":8000"
	} else {
		ip = ":8080"
	}
	fmt.Printf("Starting the server on %s...\n", ip)
	return http.ListenAndServe(ip, s.Router)
}

func main() {
	s := server.Server{
		Router: chi.NewRouter(),
	}

	err := initialize(&s)
	if err != nil {
		panic(err)
	}

	err = run(&s)
	if err != nil {
		panic(err)
	}
}
