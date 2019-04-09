// Bivac v2.0.0 (https://camptocamp.github.io/bivac)
// Copyright (c) 2019 Camptocamp
// Licensed under Apache-2.0 (https://raw.githubusercontent.com/camptocamp/bivac/master/LICENSE)
// Modifications copyright (c) 2019 Jam Risser <jam@codejam.ninja>

package main

import (
	"runtime"

	"github.com/camptocamp/volback/cmd"
	_ "github.com/camptocamp/volback/cmd/all"
	"github.com/camptocamp/volback/internal/utils"
)

var (
	exitCode  int
	buildInfo utils.BuildInfo

	// Following variables are filled in by the build script
	version    = "<<< filled in by build >>>"
	buildDate  = "<<< filled in by build >>>"
	commitSha1 = "<<< filled in by build >>>"
)

func main() {
	buildInfo.Version = version
	buildInfo.Date = buildDate
	buildInfo.CommitSha1 = commitSha1
	buildInfo.Runtime = runtime.Version()
	cmd.Execute(buildInfo)
}
