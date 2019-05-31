// Bivac v2.0.0 (https://camptocamp.github.io/bivac)
// Copyright (c) 2019 Camptocamp
// Licensed under Apache-2.0 (https://raw.githubusercontent.com/camptocamp/bivac/master/LICENSE)
// Modifications copyright (c) 2019 Jam Risser <jam@codejam.ninja>

package volume

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

var fakeHostname, _ = os.Hostname()

// SetupMetrics
func TestSetupMetrics(t *testing.T) {
	v := Volume{
		ID:         "bar",
		Name:       "bar",
		Mountpoint: "/bar",
		HostBind:   fakeHostname,
		Hostname:   fakeHostname,
		Logs:       make(map[string]string),
		BackingUp:  false,
		RepoName:   "bar",
		SubPath:    "",
	}
	v.SetupMetrics()
	assert.Equal(t, v.ID, "bar")
}
