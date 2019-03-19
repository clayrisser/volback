// Bivac v2.0.0 (https://camptocamp.github.io/bivac)
// Copyright (c) 2019 Camptocamp
// Licensed under Apache-2.0 (https://raw.githubusercontent.com/camptocamp/bivac/master/LICENSE)
// Modifications copyright (c) 2019 Jam Risser <jam@codejam.ninja>

package utils

import (
	"encoding/json"
	"io"
	"io/ioutil"
	"math/rand"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"syscall"
	"time"
)

var seededRand *rand.Rand = rand.New(rand.NewSource(time.Now().UnixNano()))

// OutputFormat stores output of Restic commands
type OutputFormat struct {
	Stdout   string `json:"stdout"`
	ExitCode int    `json:"rc"`
}

// MsgFormat is a format used to communicate with the Volback API
type MsgFormat struct {
	Type    string      `json:"type"`
	Content interface{} `json:"content"`
}

// ReturnFormattedOutput returns a formatted message
func ReturnFormattedOutput(output interface{}) string {
	m := MsgFormat{
		Type:    "success",
		Content: output,
	}
	b, err := json.Marshal(m)
	if err != nil {
		return ReturnError(err)
	}
	return string(b)
}

// ReturnError returns a formatted error
func ReturnError(e error) string {
	msg := MsgFormat{
		Type:    "error",
		Content: e.Error(),
	}
	data, _ := json.Marshal(msg)
	return string(data)
}

// HandleExitCode retrieve a command exit code from an error
func HandleExitCode(err error) int {
	if exiterr, ok := err.(*exec.ExitError); ok {
		if status, ok := exiterr.Sys().(syscall.WaitStatus); ok {
			return status.ExitStatus()
		}
	}
	return 0
}

// Recursively removes empty directory
func RemoveEmptyDir(parentPath string, cleanPath string) error {
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
		err = RemoveEmptyDir(parentPath, cleanPath)
		if err != nil {
			return err
		}
	}
	return nil
}

func GetRandomString(length int) string {
	const charset = "abcdefghijklmnopqrstuvwxyz" +
		"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	stringByte := make([]byte, length)
	for i := range stringByte {
		stringByte[i] = charset[seededRand.Intn(len(charset))]
	}
	return string(stringByte)
}

func GetRandomFolder(parentPath string) (string, error) {
	folderName := GetRandomString(16)
	randomFolderPath := parentPath + "/" + string(folderName)
	if _, err := os.Stat(randomFolderPath); !os.IsNotExist(err) {
		randomFolderPath, err = GetRandomFolder(parentPath)
		if err != nil {
			return "", err
		}
	}
	return randomFolderPath, nil
}

func MergeDirectories(sourceDir string, targetDir string) error {
	err := filepath.Walk(
		sourceDir,
		func(
			sourcePath string,
			sourceFInfo os.FileInfo,
			err error,
		) error {
			sharedPath := sourcePath[len(sourceDir):]
			if err != nil {
				return err
			}
			targetPath := targetDir + sharedPath
			if sourceFInfo.IsDir() {
				targetFInfo, err := os.Stat(targetPath)
				if err != nil {
					if !os.IsNotExist(err) {
						return err
					}
				} else {
					if !targetFInfo.IsDir() {
						err = os.Remove(targetPath)
						if err != nil {
							return err
						}
					}
				}
				os.MkdirAll(targetPath, sourceFInfo.Mode())
			} else {
				err = CopyFile(sourcePath, targetPath)
				if err != nil {
					return err
				}
			}
			return nil
		},
	)
	if err != nil {
		return err
	}
	return nil
}

func CopyFile(sourcePath string, targetPath string) error {
	sourceFInfo, err := os.Stat(sourcePath)
	if err != nil {
		return err
	}
	if !sourceFInfo.Mode().IsRegular() {
		return nil
	}
	targetFInfo, err := os.Stat(targetPath)
	if err != nil {
		if !os.IsNotExist(err) {
			return err
		}
	} else if !targetFInfo.Mode().IsRegular() {
		if targetFInfo.IsDir() {
			err := os.RemoveAll(targetPath)
			if err != nil {
				return err
			}
		} else {
			return nil
		}
	}
	if os.SameFile(sourceFInfo, targetFInfo) {
		return nil
	}
	err = os.Link(sourcePath, targetPath)
	if err != nil {
		err = copyFileContents(sourcePath, targetPath)
		if err != nil {
			return err
		}
	}
	return nil
}

func copyFileContents(sourcePath string, targetPath string) error {
	sourceFInfo, err := os.Stat(sourcePath)
	if err != nil {
		return err
	}
	sourceData, err := ioutil.ReadFile(sourcePath)
	if err != nil {
		return err
	}
	err = ioutil.WriteFile(targetPath, sourceData, sourceFInfo.Mode())
	if err != nil {
		if !os.IsNotExist(err) {
			return err
		}
	}
	return nil
}
