package main

import (
	"log/slog"
	"mergebot/handlers"
	"mergebot/webhook"
)

func init() {
	handle("!merge", MergeCmd)
	handle("!check", CheckCmd)
	handle(webhook.OnNewMR, NewMR)
}

func MergeCmd(providerName string, hook *webhook.Webhook) error {
	command, err := handlers.New(providerName)
	if err != nil {
		slog.Error("command merge", "err", err)
		return err
	}

	ok, text, err := command.Merge(hook.GetProjectID(), hook.GetID())
	if err != nil {
		slog.Error("command merge", "err", err)
		return err
	}

	if !ok && len(text) > 0 {
		return command.LeaveComment(hook.GetProjectID(), hook.GetID(), text)
	}
	return err
}

func CheckCmd(providerName string, hook *webhook.Webhook) error {
	command, err := handlers.New(providerName)
	if err != nil {
		slog.Error("command merge", "err", err)
		return err
	}

	ok, text, err := command.IsValid(hook.GetProjectID(), hook.GetID())
	if err != nil {
		slog.Error("command check", "err", err)
		return err
	}

	if !ok && len(text) > 0 {
		return command.LeaveComment(hook.GetProjectID(), hook.GetID(), text)
	} else {
		return command.LeaveComment(hook.GetProjectID(), hook.GetID(), "You can merge, LGTM :D")
	}
}

func NewMR(providerName string, hook *webhook.Webhook) error {
	command, err := handlers.New(providerName)
	if err != nil {
		slog.Error("new mr", "err", err)
		return err
	}

	err = command.Greetings(hook.GetProjectID(), hook.GetID())
	if err != nil {
		slog.Error("new mr", "err", err)
		return err
	}

	return nil
}
