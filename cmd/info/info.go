// Bivac v2.0.0 (https://camptocamp.github.io/bivac)
// Copyright (c) 2019 Camptocamp
// Licensed under Apache-2.0 (https://raw.githubusercontent.com/camptocamp/bivac/master/LICENSE)
// Modifications copyright (c) 2019 Jam Risser <jam@codejam.ninja>

package info

import (
	"fmt"
	log "github.com/Sirupsen/logrus"
	"github.com/codejamninja/volback/cmd"
	"github.com/codejamninja/volback/pkg/client"
	"github.com/spf13/cobra"
	"strings"
)

var (
	remoteAddress string
	psk           string
)

var envs = make(map[string]string)

var infoCmd = &cobra.Command{
	Use:   "info",
	Short: "Retrive Volback informations",
	Run: func(cmd *cobra.Command, args []string) {
		c, err := client.NewClient(remoteAddress, psk)
		if err != nil {
			log.Errorf("failed to create a new client: %s", err)
			return
		}

		informations, err := c.GetInformations()
		if err != nil {
			log.Errorf("failed to get informations: %s", err)
			return
		}

		for infok, infov := range informations {
			if infok == "volumes_count" {
				infok = "Managed volumes"
			}
			fmt.Printf("%s: %s\n", strings.Title(infok), infov)
		}
	},
}

func init() {
	infoCmd.Flags().StringVarP(&remoteAddress, "remote.address", "", "http://127.0.0.1:8182", "Address of the remote Volback server.")
	envs["VOLBACK_REMOTE_ADDRESS"] = "remote.address"

	infoCmd.Flags().StringVarP(&psk, "server.psk", "", "", "Pre-shared key.")
	envs["VOLBACK_SERVER_PSK"] = "server.psk"

	cmd.SetValuesFromEnv(envs, infoCmd.Flags())
	cmd.RootCmd.AddCommand(infoCmd)

}
