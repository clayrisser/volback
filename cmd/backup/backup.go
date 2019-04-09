// Bivac v2.0.0 (https://camptocamp.github.io/bivac)
// Copyright (c) 2019 Camptocamp
// Licensed under Apache-2.0 (https://raw.githubusercontent.com/camptocamp/bivac/master/LICENSE)
// Modifications copyright (c) 2019 Jam Risser <jam@codejam.ninja>

package backup

import (
	"fmt"
	"strings"

	log "github.com/Sirupsen/logrus"
	"github.com/codejamninja/volback/cmd"
	"github.com/codejamninja/volback/pkg/client"
	"github.com/spf13/cobra"
	"github.com/tatsushid/go-prettytable"
)

var (
	remoteAddress string
	psk           string
	force         bool
)

var envs = make(map[string]string)

var backupCmd = &cobra.Command{
	Use:   "backup [VOLUME_NAME]",
	Short: "Backup volumes",
	Args:  cobra.MinimumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		c, err := client.NewClient(remoteAddress, psk)
		if err != nil {
			log.Errorf("failed to create new client: %s", err)
			return
		}

		for _, a := range args {
			fmt.Printf("Backing up `%s'...\n", a)
			err = c.BackupVolume(a, force)
			if err != nil {
				log.Errorf("failed to backup volume: %s", err)
				return
			}
		}

		volumes, err := c.GetVolumes()
		if err != nil {
			log.Errorf("failed to get volumes: %s", err)
			return
		}

		for _, a := range args {
			for _, v := range volumes {
				if v.ID == a {
					tbl, err := prettytable.NewTable([]prettytable.Column{
						{},
						{},
						{},
					}...)
					if err != nil {
						log.WithFields(log.Fields{
							"volume":   v.Name,
							"hostname": v.Hostname,
						}).Errorf("failed to format output: %s", err)
						return
					}
					tbl.Separator = "\t"

					fmt.Printf("ID: %s\n", v.ID)
					fmt.Printf("Name: %s\n", v.Name)
					fmt.Printf("Mountpoint: %s\n", v.Mountpoint)
					fmt.Printf("Backup date: %s\n", v.LastBackupDate)
					fmt.Printf("Backup status: %s\n", v.LastBackupStatus)
					fmt.Printf("Logs:\n")
					tbl.AddRow("", "testInit", strings.Replace(v.Logs["testInit"], "\n", "\n\t\t\t", -1))
					tbl.AddRow("", "init", strings.Replace(v.Logs["init"], "\n", "\n\t\t\t", -1))
					tbl.AddRow("", "backup", strings.Replace(v.Logs["backup"], "\n", "\n\t\t\t", -1))
					tbl.AddRow("", "forget", strings.Replace(v.Logs["forget"], "\n", "\n\t\t\t", -1))
					tbl.Print()
				}
			}
		}
	},
}

func init() {
	backupCmd.Flags().StringVarP(&remoteAddress, "remote.address", "", "http://127.0.0.1:8182", "Address of the remote Volback server.")
	envs["VOLBACK_REMOTE_ADDRESS"] = "remote.address"

	backupCmd.Flags().StringVarP(&psk, "server.psk", "", "", "Pre-shared key.")
	envs["VOLBACK_SERVER_PSK"] = "server.psk"

	backupCmd.Flags().BoolVarP(&force, "force", "", false, "Force backup by removing locks.")

	cmd.SetValuesFromEnv(envs, backupCmd.Flags())
	cmd.RootCmd.AddCommand(backupCmd)
}
