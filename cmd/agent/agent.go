package agent

import (
	"github.com/spf13/cobra"

	"github.com/codejamninja/bivac/cmd"
	"github.com/codejamninja/bivac/internal/agent"
)

var (
	targetURL   string
	backupPath  string
	hostname    string
	force       bool
	logReceiver string
)

var agentCmd = &cobra.Command{
	Use:   "agent",
	Short: "Run Bivac agent",
	Run: func(cmd *cobra.Command, args []string) {
		switch args[0] {
		case "backup":
			agent.Backup(targetURL, backupPath, hostname, force, logReceiver)
		case "restore":
			agent.Restore(targetURL, backupPath, hostname, force, logReceiver)
		}
	},
}

func init() {
	agentCmd.Flags().StringVarP(&targetURL, "target.url", "r", "", "The target URL to push the backups to.")
	agentCmd.Flags().StringVarP(&backupPath, "backup.path", "p", "", "Path to the volume to backup.")
	agentCmd.Flags().StringVarP(&hostname, "host", "", "", "Custom hostname.")
	agentCmd.Flags().BoolVarP(&force, "force", "", false, "Force a backup by removing all locks.")
	agentCmd.Flags().StringVarP(&logReceiver, "log.receiver", "", "", "Address where the manager will collect the logs.")
	cmd.RootCmd.AddCommand(agentCmd)
}
