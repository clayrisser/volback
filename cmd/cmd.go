// Bivac v2.0.0 (https://camptocamp.github.io/bivac)
// Copyright (c) 2019 Camptocamp
// Licensed under Apache-2.0 (https://raw.githubusercontent.com/camptocamp/bivac/master/LICENSE)
// Modifications copyright (c) 2019 Jam Risser <jam@codejam.ninja>

package cmd

import (
	"fmt"
	"github.com/codejamninja/volback/internal/utils"
	"github.com/spf13/cobra"
	"github.com/spf13/pflag"
	"github.com/spf13/viper"
	"os"
	log "github.com/Sirupsen/logrus"
)

var (
	verbose   bool
	whitelist string
	blacklist string

	// BuildInfo contains the Volback build informations (filled by main.go at build time)
	BuildInfo utils.BuildInfo
)

var persistentEnvs = make(map[string]string)
var localEnvs = make(map[string]string)

// RootCmd is a global variable which will handle all subcommands
var RootCmd = &cobra.Command{
	Use: "volback",
}

func initConfig() {
	if verbose {
		log.SetLevel(log.DebugLevel)
	}
}

func init() {
	cobra.OnInitialize(initConfig)
	viper.AutomaticEnv()
	RootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "Enable verbose output")
	localEnvs["VOLBACK_VERBOSE"] = "verbose"
	RootCmd.PersistentFlags().StringVarP(&whitelist, "whitelist", "w", "", "Only backup whitelisted volumes.")
	localEnvs["VOLBACK_VOLUMES_WHITELIST"] = "whitelist"
	RootCmd.PersistentFlags().StringVarP(&blacklist, "blacklist", "b", "", "Do not backup blacklisted volumes.")
	localEnvs["VOLBACK_VOLUMES_BLACKLIST"] = "blacklist"

	SetValuesFromEnv(localEnvs, RootCmd.PersistentFlags())
	SetValuesFromEnv(persistentEnvs, RootCmd.PersistentFlags())
}

// Execute is the main thread, required by Cobra
func Execute(buildInfo utils.BuildInfo) {
	BuildInfo = buildInfo
	if err := RootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

// SetValuesFromEnv assigns values to Cobra variables from environment variables
func SetValuesFromEnv(envs map[string]string, flags *pflag.FlagSet) {
	for env, flag := range envs {
		flag := flags.Lookup(flag)
		flag.Usage = fmt.Sprintf("%v [%v]", flag.Usage, env)
		if value := os.Getenv(env); value != "" {
			flag.Value.Set(value)
		} else {
			os.Setenv(env, flag.Value.String())
		}
	}
	return
}
