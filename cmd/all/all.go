package all

import (
	// Run a Bivac agent
	_ "github.com/codejamninja/bivac/cmd/agent"
	// Backup a volume
	_ "github.com/codejamninja/bivac/cmd/backup"
	// Get informations regarding the Bivac manager
	_ "github.com/codejamninja/bivac/cmd/info"
	// Run a Bivac manager
	_ "github.com/codejamninja/bivac/cmd/manager"
	// Run a custom Restic command on a volume's remote repository
	_ "github.com/codejamninja/bivac/cmd/restic"
	// List volumes and display informations regarding the backed up volumes
	_ "github.com/codejamninja/bivac/cmd/volumes"
)
