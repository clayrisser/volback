// Bivac v2.0.0 (https://camptocamp.github.io/bivac)
// Copyright (c) 2019 Camptocamp
// Licensed under Apache-2.0 (https://raw.githubusercontent.com/camptocamp/bivac/master/LICENSE)
// Modifications copyright (c) 2019 Jam Risser <jam@codejam.ninja>

package all

import (
	// Run a Volback agent
	_ "github.com/codejamninja/volback/cmd/agent"
	// Backup a volume
	_ "github.com/codejamninja/volback/cmd/backup"
	// Restore a volume
	_ "github.com/codejamninja/volback/cmd/restore"
	// Get informations regarding the Volback manager
	_ "github.com/codejamninja/volback/cmd/info"
	// Run a Volback manager
	_ "github.com/codejamninja/volback/cmd/manager"
	// Run a custom Restic command on a volume's remote repository
	_ "github.com/codejamninja/volback/cmd/restic"
	// List volumes and display informations regarding the backed up volumes
	_ "github.com/codejamninja/volback/cmd/volumes"
)
