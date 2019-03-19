// Bivac v2.0.0 (https://camptocamp.github.io/bivac)
// Copyright (c) 2019 Camptocamp
// Licensed under Apache-2.0 (https://raw.githubusercontent.com/camptocamp/bivac/master/LICENSE)
// Modifications copyright (c) 2019 Jam Risser <jam@codejam.ninja>

package engine

import (
	"encoding/json"
	"github.com/codejamninja/volback/internal/utils"
	"io"
	"io/ioutil"
	"math/rand"
	"os"
	"os/exec"
	"regexp"
	"strings"
	"time"
)

var seededRand *rand.Rand = rand.New(rand.NewSource(time.Now().UnixNano()))

// Engine stores informations to use Restic backup engine
type Engine struct {
	DefaultArgs []string
	Output      map[string]utils.OutputFormat
}

// Snapshot is a struct returned by the function snapshots()
type Snapshot struct {
	Time     time.Time `json:"time"`
	Parent   string    `json:"parent"`
	Tree     string    `json:"tree"`
	Path     []string  `json:"path"`
	Hostname string    `json:"hostname"`
	ID       string    `json:"id"`
	ShortID  string    `json:"short_id"`
}

// GetName returns the engine name
func (*Engine) GetName() string {
	return "restic"
}

// Backup performs the backup of the passed volume
func (r *Engine) Backup(backupPath, hostname string, force bool) string {
	var err error
	err = r.initializeRepository()
	if err != nil {
		return utils.ReturnFormattedOutput(r.Output)
	}
	if force {
		err = r.unlockRepository()
		if err != nil {
			return utils.ReturnFormattedOutput(r.Output)
		}
	}
	err = r.backupVolume(hostname, backupPath)
	if err != nil {
		return utils.ReturnFormattedOutput(r.Output)
	}
	err = r.forget()
	if err != nil {
		return utils.ReturnFormattedOutput(r.Output)
	}
	err = r.retrieveBackupsStats()
	if err != nil {
		return utils.ReturnFormattedOutput(r.Output)
	}
	return utils.ReturnFormattedOutput(r.Output)
}

// Restore performs the restore of the passed volume
func (r *Engine) Restore(
	backupPath,
	hostname string,
	force bool,
	snapshotName string,
) string {
	var err error
	if force {
		err = r.unlockRepository()
		if err != nil {
			return utils.ReturnFormattedOutput(r.Output)
		}
	}
	err = r.restoreVolume(hostname, backupPath, snapshotName)
	if err != nil {
		return utils.ReturnFormattedOutput(r.Output)
	}
	err = r.retrieveBackupsStats()
	if err != nil {
		return utils.ReturnFormattedOutput(r.Output)
	}
	return utils.ReturnFormattedOutput(r.Output)
}

func (r *Engine) initializeRepository() (err error) {
	rc := 0
	// Check if the remote repository exists
	output, err := exec.Command(
		"restic",
		append(r.DefaultArgs, "snapshots")...,
	).CombinedOutput()
	if err != nil {
		rc = utils.HandleExitCode(err)
	}
	if rc == 0 {
		return
	}
	r.Output["testInit"] = utils.OutputFormat{
		Stdout:   string(output),
		ExitCode: rc,
	}
	err = nil
	rc = 0
	// Create remote repository
	output, err = exec.Command(
		"restic",
		append(r.DefaultArgs, "init")...,
	).CombinedOutput()
	if err != nil {
		rc = utils.HandleExitCode(err)
	}
	r.Output["init"] = utils.OutputFormat{
		Stdout:   string(output),
		ExitCode: rc,
	}
	err = nil
	return
}

func (r *Engine) backupVolume(hostname, backupPath string) (err error) {
	rc := 0
	output, err := exec.Command(
		"restic",
		append(r.DefaultArgs, []string{
			"--host",
			hostname,
			"backup",
			backupPath,
		}...)...,
	).CombinedOutput()
	if err != nil {
		rc = utils.HandleExitCode(err)
	}
	r.Output["backup"] = utils.OutputFormat{
		Stdout:   string(output),
		ExitCode: rc,
	}
	err = nil
	return
}

func (r *Engine) restoreVolume(
	hostname,
	backupPath string,
	snapshotName string,
) (err error) {
	rc := 0
	origionalBackupPath := r.getOrigionalBackupPath(
		hostname,
		backupPath,
		snapshotName,
	)
	workingPath, err := r.createRandomFolder(backupPath)
	if err != nil {
		rc = utils.HandleExitCode(err)
	}
	output, err := exec.Command(
		"restic",
		append(
			r.DefaultArgs,
			[]string{
				"--host",
				hostname,
				"restore",
				snapshotName,
				"--target",
				workingPath,
			}...,
		)...,
	).CombinedOutput()
	restoreDumpPath := workingPath + origionalBackupPath
	files, err := ioutil.ReadDir(restoreDumpPath)
	if err != nil {
		rc = utils.HandleExitCode(err)
	}
	collisionPath := ""
	for _, f := range files {
		restorePath := backupPath + "/" + f.Name()
		if restorePath == workingPath {
			// tmpRandomBackupPath, err :=
			// 	r.createRandomFolder(randomBackupPath)
			// if err != nil {
			// 	rc = utils.HandleExitCode(err)
			// }
			// restorePath = tmpRandomBackupPath + "/" + f.Name()
			// randomBackupPathCollision = restorePath
		} else {
			if _, err := os.Stat(restorePath); !os.IsNotExist(err) {
				err = os.RemoveAll(restorePath)
				if err != nil {
					rc = utils.HandleExitCode(err)
				}
			}
		}
		os.Rename(
			restoreDumpPath+"/"+f.Name(),
			restorePath,
		)
	}
	err = r.removeEmptyDir(backupPath, restoreDumpPath)
	if err != nil {
		rc = utils.HandleExitCode(err)
	}
	if len(collisionPath) > 0 {
		// tmpBackupPath, err :=
		// 	r.createRandomFolder(backupPath)
		// if err != nil {
		// 	rc = utils.HandleExitCode(err)
		// }
		// collisionPath := tmpBackupPath + "/collision"
		// os.Rename(
		// 	randomBackupPathCollision,
		// 	collisionPath,
		// )
		// err = os.MkdirAll(randomBackupPathCollision, 0700)
		// if err != nil {
		// 	rc = utils.HandleExitCode(err)
		// }
		// err = r.removeEmptyDir(
		// 	backupPath,
		// 	randomBackupPathCollision[len(backupPath):],
		// )
		// if err != nil {
		// 	rc = utils.HandleExitCode(err)
		// }
		// os.Rename(
		// 	collisionPath,
		// 	randomBackupPath,
		// )
		// err = r.removeEmptyDir(
		// 	backupPath,
		// 	collisionPath[len(backupPath):],
		// )
		// if err != nil {
		// 	rc = utils.HandleExitCode(err)
		// }
	}
	r.Output["restore"] = utils.OutputFormat{
		Stdout:   string(output),
		ExitCode: rc,
	}
	err = nil
	return
}

func (r *Engine) getOrigionalBackupPath(
	hostname,
	backupPath string,
	snapshotName string,
) string {
	output, err := exec.Command(
		"restic",
		append(
			r.DefaultArgs,
			[]string{"--host", hostname, "ls", snapshotName}...,
		)...,
	).CombinedOutput()
	type Header struct {
		Paths []string `json:"paths"`
	}
	headerJson := []byte(strings.Split(string(output), "\n")[1])
	var header Header
	err = json.Unmarshal(headerJson, &header)
	if err != nil {
		return "/"
	}
	return header.Paths[0]
}

func (r *Engine) createRandomFolder(parentPath string) (string, error) {
	const charset = "abcdefghijklmnopqrstuvwxyz" +
		"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	folderName := make([]byte, 16)
	for i := range folderName {
		folderName[i] = charset[seededRand.Intn(len(charset))]
	}
	randomFolderPath := parentPath + "/" + string(folderName)
	if _, err := os.Stat(randomFolderPath); !os.IsNotExist(err) {
		randomFolderPath, err = r.createRandomFolder(parentPath)
		if err != nil {
			return "", err
		}
	}
	err := os.MkdirAll(randomFolderPath, 0700)
	if err != nil {
		return "", err
	}
	return randomFolderPath, nil
}

func (r *Engine) removeEmptyDir(parentPath string, cleanPath string) error {
	if len(cleanPath) >= len(parentPath) &&
		parentPath == cleanPath[:len(parentPath)] {
		cleanPath = cleanPath[len(parentPath):]
	}
	match := ""
	re := regexp.MustCompile(`((\\\/)|[^\/])+$`)
	if len(re.FindStringIndex(cleanPath)) > 0 {
		match = re.FindString(cleanPath)
	}
	fullCleanPath := parentPath + cleanPath
	fileInfo, err := os.Stat(fullCleanPath)
	if err != nil {
		return err
	}
	if !fileInfo.IsDir() {
		return nil
	}
	f, err := os.Open(fullCleanPath)
	if err != nil {
		return err
	}
	_, err = f.Readdir(1)
	if err != io.EOF {
		return nil
	}
	f.Close()
	err = os.Remove(fullCleanPath)
	if err != nil {
		return err
	}
	cleanPath = cleanPath[0 : len(cleanPath)-len(match)-1]
	if len(cleanPath) > 0 {
		err = r.removeEmptyDir(parentPath, cleanPath)
		if err != nil {
			return err
		}
	}
	return nil
}

func (r *Engine) forget() (err error) {
	rc := 0
	cmd := append(r.DefaultArgs, "forget")
	cmd = append(
		cmd,
		strings.Split(os.Getenv("RESTIC_FORGET_ARGS"), " ")...,
	)
	output, err := exec.Command("restic", cmd...).CombinedOutput()
	if err != nil {
		rc = utils.HandleExitCode(err)
	}
	r.Output["forget"] = utils.OutputFormat{
		Stdout:   string(output),
		ExitCode: rc,
	}
	err = nil
	return
}

func (r *Engine) retrieveBackupsStats() (err error) {
	rc := 0
	output, err := exec.Command(
		"restic",
		append(r.DefaultArgs, []string{"snapshots"}...)...,
	).CombinedOutput()
	if err != nil {
		rc = utils.HandleExitCode(err)
	}
	r.Output["snapshots"] = utils.OutputFormat{
		Stdout:   string(output),
		ExitCode: rc,
	}
	return
}

func (r *Engine) unlockRepository() (err error) {
	rc := 0
	output, err := exec.Command(
		"restic",
		append(r.DefaultArgs, []string{"unlock", "--remove-all"}...)...,
	).CombinedOutput()
	if err != nil {
		rc = utils.HandleExitCode(err)
	}
	r.Output["unlock"] = utils.OutputFormat{
		Stdout:   string(output),
		ExitCode: rc,
	}
	err = nil
	return
}

// GetBackupDates runs a Restic command locally to retrieve latest snapshot date
func (r *Engine) GetBackupDates() (
	latestSnapshotDate,
	oldestSnapshotDate time.Time,
	err error,
) {
	output, _ := exec.Command(
		"restic",
		append(r.DefaultArgs, []string{"snapshots"}...)...,
	).CombinedOutput()
	var data []Snapshot
	err = json.Unmarshal(output, &data)
	if err != nil {
		return
	}
	if len(data) == 0 {
		return
	}
	latestSnapshot := data[len(data)-1]
	latestSnapshotDate = latestSnapshot.Time
	if err != nil {
		return
	}
	oldestSnapshot := data[0]
	oldestSnapshotDate = oldestSnapshot.Time
	if err != nil {
		return
	}
	return
}

// RawCommand runs a custom Restic command locally
func (r *Engine) RawCommand(cmd []string) (err error) {
	rc := 0
	output, err := exec.Command(
		"restic",
		append(r.DefaultArgs, cmd...)...,
	).CombinedOutput()
	if err != nil {
		rc = utils.HandleExitCode(err)
	}
	r.Output["raw"] = utils.OutputFormat{
		Stdout:   string(output),
		ExitCode: rc,
	}
	return
}
