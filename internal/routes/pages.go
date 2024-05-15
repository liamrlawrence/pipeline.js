package routes

import (
	"net/http"

	"github.com/liamrlawrence/nodejs/site/internal/pages/views"
	"github.com/liamrlawrence/nodejs/site/internal/server"
)

// Demo page
func demoPageHandler(s *server.Server) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		component := views.PageDemo()
		component.Render(r.Context(), w)
	}
}
