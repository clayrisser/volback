// Bivac v2.0.0 (https://camptocamp.github.io/bivac)
// Copyright (c) 2019 Camptocamp
// Licensed under Apache-2.0 (https://raw.githubusercontent.com/camptocamp/bivac/master/LICENSE)
// Modifications copyright (c) 2019 Jam Risser <jam@codejam.ninja>

package orchestrators

import (
	"github.com/codejamninja/bivac/pkg/volume"
)

// Orchestrator implements a container Orchestrator interface
type Orchestrator interface {
	GetName() string
	GetPath(v *volume.Volume) string
	GetVolumes(volumeFilters volume.Filters) (volumes []*volume.Volume, err error)
	DeployAgent(image string, cmd []string, envs []string, volume *volume.Volume) (success bool, output string, err error)
	GetContainersMountingVolume(v *volume.Volume) (mountedVolumes []*volume.MountedVolume, err error)
	ContainerExec(mountedVolumes *volume.MountedVolume, command []string) (stdout string, err error)
	IsNodeAvailable(hostID string) (ok bool, err error)
}
