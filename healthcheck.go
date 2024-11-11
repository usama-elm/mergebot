package main

import (
	"net/http"

	"github.com/labstack/echo/v4"
)

//nolint:errcheck
func healthcheck(c echo.Context) error {
	c.String(http.StatusOK, "ok")
	return nil
}
