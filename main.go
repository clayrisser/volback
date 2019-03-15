// Modifications copyright (c) 2019 Jam Risser <jam@codejam.ninja>

package main

import (
	"github.com/codejamninja/bivac/cmd"
	_ "github.com/codejamninja/bivac/cmd/all"
)

var exitCode int

// Following variables are filled in by the build script
var version = "<<< filled in by build >>>"

func main() {
	cmd.Execute(version)
}
