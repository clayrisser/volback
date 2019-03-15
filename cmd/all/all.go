// Bivac v2.0.0 (https://camptocamp.github.io/bivac)
// Copyright (c) 2019 Camptocamp
// Licensed under Apache-2.0 (https://raw.githubusercontent.com/camptocamp/bivac/master/LICENSE)
// Modifications copyright (c) 2019 Jam Risser <jam@codejam.ninja>

package all

import (
	// Run a Bivac agent
	_ "github.com/codejamninja/bivac/cmd/agent"
	// Backup a volume
	_ "github.com/codejamninja/bivac/cmd/backup"
	// Restore a volume
	_ "github.com/codejamninja/bivac/cmd/restore"
	// Get informations regarding the Bivac manager
	_ "github.com/codejamninja/bivac/cmd/info"
	// Run a Bivac manager
	_ "github.com/codejamninja/bivac/cmd/manager"
	// Run a custom Restic command on a volume's remote repository
	_ "github.com/codejamninja/bivac/cmd/restic"
	// List volumes and display informations regarding the backed up volumes
	_ "github.com/codejamninja/bivac/cmd/volumes"
)
