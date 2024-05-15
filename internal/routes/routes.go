package routes

import (
	"fmt"
	"net/http"
	"path/filepath"

	"github.com/go-chi/chi/v5"
	"github.com/liamrlawrence/nodejs/site/internal/server"
)

func SetupRouter(s *server.Server) {
	// API routes
	s.Router.Group(func(r chi.Router) {
		r.Use(LogRouteMiddleware)

		// System
		r.Get("/api/system/status", HandlerRouteStatus(s))
	})

	// Static File routes
	s.Router.Group(func(r chi.Router) {
		//r.Use(LogRouteMiddleware)
		r.Get("/static/*", func(w http.ResponseWriter, r *http.Request) {
			fileExt := filepath.Ext(r.URL.Path)
			switch fileExt {
			case ".js":
				w.Header().Set("Content-Type", "application/javascript; charset=utf-8")
			case ".css":
				w.Header().Set("Content-Type", "text/css; charset=utf-8")
			}
			http.StripPrefix("/static/", http.FileServer(http.Dir("/app/static"))).ServeHTTP(w, r)
		})
	})

	// Pages
	s.Router.Group(func(r chi.Router) {
		r.Get("/", demoPageHandler(s))
	})

	// 404
	s.Router.NotFound(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, "Page not found", http.StatusNotFound)
	})
}

func HandlerRouteStatus(s *server.Server) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		fmt.Fprint(w, `{
    "status": 200,
    "message": "OK"
}`)
		return
	}
}
