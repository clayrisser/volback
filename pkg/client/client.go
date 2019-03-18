// Bivac v2.0.0 (https://camptocamp.github.io/bivac)
// Copyright (c) 2019 Camptocamp
// Licensed under Apache-2.0 (https://raw.githubusercontent.com/camptocamp/bivac/master/LICENSE)
// Modifications copyright (c) 2019 Jam Risser <jam@codejam.ninja>

package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"github.com/codejamninja/volback/pkg/volume"
	"io/ioutil"
	"net/http"
	"strconv"
)

// Client contains informations needed to connect to a Volback API
type Client struct {
	remoteAddress string
	psk           string
}

// NewClient returns a Volback client
func NewClient(remoteAddress string, psk string) (c *Client, err error) {
	c = &Client{
		remoteAddress: remoteAddress,
		psk:           psk,
	}

	var pingResponse map[string]string
	err = c.newRequest(&pingResponse, "GET", "/ping", "")
	if err != nil {
		err = fmt.Errorf("failed to connect to the remote Volback instance: %s", err)
		return
	}
	if pingResponse["type"] != "pong" {
		err = fmt.Errorf("wrong response from the Volback instance: %v", pingResponse)
		return
	}
	return
}

// GetVolumes returns the list of the volumes managed by Volback
func (c *Client) GetVolumes() (volumes []volume.Volume, err error) {
	err = c.newRequest(&volumes, "GET", "/volumes", "")
	if err != nil {
		err = fmt.Errorf("failed to connect to the remote Volback instance: %s", err)
		return
	}
	return
}

// BackupVolume requests a backup of a volume
func (c *Client) BackupVolume(volumeName string, force bool) (err error) {
	err = c.newRequest(nil, "POST", fmt.Sprintf("/backup/%s?force=%s", volumeName, strconv.FormatBool(force)), "")
	if err != nil {
		err = fmt.Errorf("failed to connect to the remote Volback instance: %s", err)
		return
	}
	return
}

// RestoreVolume requests a restore of a volume
func (c *Client) RestoreVolume(
	volumeName string,
	force bool,
	snapshotName string,
) (err error) {
	err = c.newRequest(
		nil,
		"POST",
		fmt.Sprintf(
			"/restore/%s/%s?force=%s",
			volumeName,
			snapshotName,
			strconv.FormatBool(force),
		),
		"",
	)
	if err != nil {
		err = fmt.Errorf(
			"failed to connect to the remote Volback instance: %s",
			err,
		)
		return
	}
	return
}

// RunRawCommand runs a custom Restic command on a volume's repository and returns the output
func (c *Client) RunRawCommand(volumeID string, cmd []string) (output string, err error) {
	var response map[string]interface{}

	postValue := make(map[string][]string)
	postValue["cmd"] = cmd

	postValueEncoded, _ := json.Marshal(postValue)

	err = c.newRequest(&response, "POST", fmt.Sprintf("/restic/%s", volumeID), string(postValueEncoded))
	if err != nil {
		err = fmt.Errorf("failed to connect to the remote Volback instance: %s", err)
		return
	}

	output = response["data"].(string)
	return
}

// GetInformations returns informations about the Volback manager
func (c *Client) GetInformations() (informations map[string]string, err error) {
	var data struct {
		Type string `json:"type"`
		Data map[string]string
	}
	err = c.newRequest(&data, "GET", "/info", "")
	if err != nil {
		err = fmt.Errorf("failed to connect to the remote Volback instance: %s", err)
		return
	}
	informations = data.Data
	return
}

func (c *Client) newRequest(data interface{}, method, endpoint, value string) (err error) {
	client := &http.Client{}
	req, err := http.NewRequest(method, c.remoteAddress+endpoint, bytes.NewBuffer([]byte(value)))
	if err != nil {
		err = fmt.Errorf("failed to build request: %s", err)
		return
	}

	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", c.psk))

	res, err := client.Do(req)
	if err != nil {
		err = fmt.Errorf("failed to send request: %s", err)
		return
	}
	defer res.Body.Close()

	body, err := ioutil.ReadAll(res.Body)
	if err != nil {
		err = fmt.Errorf("failed to read body: %s", err)
		return
	}

	if res.StatusCode == http.StatusOK {
		if err := json.Unmarshal(body, &data); err != nil {
			err = fmt.Errorf("failed to unmarshal response from the Volback instance: %s", err)
			return err
		}
	} else {
		err = fmt.Errorf("received wrong status code from the Volback instance: [%d] %s", res.StatusCode, string(body))
		return
	}
	return
}
