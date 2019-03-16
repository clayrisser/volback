// Bivac v2.0.0 (https://camptocamp.github.io/bivac)
// Copyright (c) 2019 Camptocamp
// Licensed under Apache-2.0 (https://raw.githubusercontent.com/camptocamp/bivac/master/LICENSE)
// Modifications copyright (c) 2019 Jam Risser <jam@codejam.ninja>

package agent

import (
	"bytes"
	"fmt"
	log "github.com/Sirupsen/logrus"
	"github.com/codejamninja/volback/internal/engine"
	"github.com/codejamninja/volback/internal/utils"
	"io/ioutil"
	"net/http"
	"os"
)

// Backup runs Restic commands to backup a volume
func Backup(targetURL, backupPath, hostname string, force bool, logReceiver string) {
	e := &engine.Engine{
		DefaultArgs: []string{
			"--no-cache",
			"--json",
			"-r",
			targetURL,
		},
		Output: make(map[string]utils.OutputFormat),
	}
	output := e.Backup(backupPath, hostname, force)
	if logReceiver != "" {
		data := `{"data":` + output + `}`
		req, err := http.NewRequest("POST", logReceiver, bytes.NewBuffer([]byte(data)))
		if err != nil {
			log.Errorf("failed to build new request: %s\n", err)
			return
		}
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Authorization", "Bearer "+os.Getenv("VOLBACK_SERVER_PSK"))
		client := &http.Client{}
		resp, err := client.Do(req)
		if err != nil {
			log.Errorf("failed to send data: %s\n", err)
			return
		}
		defer resp.Body.Close()
		b, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			log.Errorf("failed to read body: %s\n", err)
			return
		}
		if resp.StatusCode != 200 {
			log.Infof("Response from API: %s", b)
		}
		return
	}
	fmt.Println(output)
	return
}

// Restore runs Restic commands to restore backed up data to a new volume
func Restore(targetURL, backupPath, hostname string, force bool, logReceiver string) {
	e := &engine.Engine{
		DefaultArgs: []string{
			"--no-cache",
			"--json",
			"-r",
			targetURL,
		},
		Output: make(map[string]utils.OutputFormat),
	}
	output := e.Restore(backupPath, hostname, force)
	if logReceiver != "" {
		data := `{"data":` + output + `}`
		req, err := http.NewRequest("POST", logReceiver, bytes.NewBuffer([]byte(data)))
		if err != nil {
			log.Errorf("failed to build new request: %s\n", err)
			return
		}
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Authorization", "Bearer "+os.Getenv("VOLBACK_SERVER_PSK"))
		client := &http.Client{}
		resp, err := client.Do(req)
		if err != nil {
			log.Errorf("failed to send data: %s\n", err)
			return
		}
		defer resp.Body.Close()
		b, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			log.Errorf("failed to read body: %s\n", err)
			return
		}
		if resp.StatusCode != 200 {
			log.Infof("Response from API: %s", b)
		}
		return
	}
	fmt.Println(output)
	return
}
