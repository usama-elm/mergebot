package main

import (
	"log/slog"
	_ "mergebot/handlers/gitlab"
	_ "mergebot/webhook/gitlab"
	// _ "mergebot/metrics"
)

func main() {
	slog.SetLogLoggerLevel(slog.LevelDebug)
	start()
}
