package routes

import (
	"fmt"
	"net/http"
)

func LogRouteMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fmt.Println("Accessed Route: ", r.URL.Path)
		next.ServeHTTP(w, r)
	})
}
