// Bivac v2.0.0 (https://camptocamp.github.io/bivac)
// Copyright (c) 2019 Camptocamp
// Licensed under Apache-2.0 (https://raw.githubusercontent.com/camptocamp/bivac/master/LICENSE)
// Modifications copyright (c) 2019 Jam Risser <jam@codejam.ninja>

package manager

import (
	"strings"

	log "github.com/Sirupsen/logrus"
	"github.com/spf13/cobra"

	volbackCmd "github.com/codejamninja/volback/cmd"
	"github.com/codejamninja/volback/internal/manager"
	"github.com/codejamninja/volback/pkg/volume"
)

var (
	server       manager.Server
	orchestrator string

	// Orchestrators is a copy of manager.Orchestrators which allows orchestrator
	// configuration from Cobra variables
	Orchestrators manager.Orchestrators

	dbPath           string
	resticForgetArgs string

	providersFile       string
	targetURL           string
	retryCount          int
	logServer           string
	agentImage          string
	whitelistVolumes    string
	blacklistVolumes    string
	whitelistAnnotation bool
)
var envs = make(map[string]string)

var managerCmd = &cobra.Command{
	Use:   "manager",
	Short: "Start Volback backup manager",
	Run: func(cmd *cobra.Command, args []string) {
		volumesFilters := volume.Filters{
			Blacklist:           strings.Split(blacklistVolumes, ","),
			Whitelist:           strings.Split(whitelistVolumes, ","),
			WhitelistAnnotation: whitelistAnnotation,
		}

		o, err := manager.GetOrchestrator(orchestrator, Orchestrators)
		if err != nil {
			log.Errorf("failed to retrieve orchestrator: %s", err)
			return
		}

		err = manager.Start(volbackCmd.BuildInfo, o, server, volumesFilters, providersFile, targetURL, logServer, agentImage, retryCount)
		if err != nil {
			log.Errorf("failed to start manager: %s", err)
			return
		}
	},
}

func init() {
	managerCmd.Flags().StringVarP(&server.Address, "server.address", "", "0.0.0.0:8182", "Address to bind on.")
	envs["VOLBACK_SERVER_ADDRESS"] = "server.address"
	managerCmd.Flags().StringVarP(&server.PSK, "server.psk", "", "", "Pre-shared key.")
	envs["VOLBACK_SERVER_PSK"] = "server.psk"

	managerCmd.Flags().StringVarP(&orchestrator, "orchestrator", "o", "", "Orchestrator on which Volback should connect to.")
	envs["VOLBACK_ORCHESTRATOR"] = "orchestrator"

	managerCmd.Flags().StringVarP(&Orchestrators.Docker.Endpoint, "docker.endpoint", "", "unix:///var/run/docker.sock", "Docker endpoint.")
	envs["VOLBACK_DOCKER_ENDPOINT"] = "docker.endpoint"

	managerCmd.Flags().StringVarP(&Orchestrators.Cattle.URL, "cattle.url", "", "", "The Cattle URL.")
	envs["CATTLE_URL"] = "cattle.url"
	managerCmd.Flags().StringVarP(&Orchestrators.Cattle.AccessKey, "cattle.accesskey", "", "", "The Cattle access key.")
	envs["CATTLE_ACCESS_KEY"] = "cattle.accesskey"
	managerCmd.Flags().StringVarP(&Orchestrators.Cattle.SecretKey, "cattle.secretkey", "", "", "The Cattle secret key.")
	envs["CATTLE_SECRET_KEY"] = "cattle.secretkey"

	managerCmd.Flags().StringVarP(&Orchestrators.Kubernetes.Namespace, "kubernetes.namespace", "", "", "Namespace where you want to run Volback.")
	envs["KUBERNETES_NAMESPACE"] = "kubernetes.namespace"
	managerCmd.Flags().BoolVarP(&Orchestrators.Kubernetes.AllNamespaces, "kubernetes.all-namespaces", "", false, "Backup volumes of all namespaces.")
	envs["KUBERNETES_ALL_NAMESPACES"] = "kubernetes.all-namespaces"
	managerCmd.Flags().StringVarP(&Orchestrators.Kubernetes.KubeConfig, "kubernetes.kubeconfig", "", "", "Path to your kuberconfig file.")
	envs["KUBERNETES_KUBECONFIG"] = "kubernetes.kubeconfig"
	managerCmd.Flags().StringVarP(&Orchestrators.Kubernetes.AgentServiceAccount, "kubernetes.agent-service-account", "", "", "Specify service account for agents.")
	envs["KUBERNETES_AGENT_SERVICE_ACCOUNT"] = "kubernetes.agent-service-account"

	managerCmd.Flags().StringVarP(&resticForgetArgs, "restic.forget.args", "", "--group-by host --keep-daily 15 --prune", "Restic forget arguments.")
	envs["RESTIC_FORGET_ARGS"] = "restic.forget.args"

	managerCmd.Flags().StringVarP(&providersFile, "providers.config", "", "/providers-config.default.toml", "Configuration file for providers.")
	envs["VOLBACK_PROVIDERS_CONFIG"] = "providers.config"

	managerCmd.Flags().StringVarP(&targetURL, "target.url", "r", "", "The target URL to push the backups to.")
	envs["VOLBACK_TARGET_URL"] = "target.url"

	managerCmd.Flags().IntVarP(&retryCount, "retry.count", "", 0, "Retry to backup the volume if something goes wrong with Volback.")
	envs["VOLBACK_RETRY_COUNT"] = "retry.count"

	managerCmd.Flags().StringVarP(&logServer, "log.server", "", "", "Manager's API address that will receive logs from agents.")
	envs["VOLBACK_LOG_SERVER"] = "log.server"

	managerCmd.Flags().StringVarP(&agentImage, "agent.image", "", "codejamninja/volback:2.0", "Agent's Docker image.")
	envs["VOLBACK_AGENT_IMAGE"] = "agent.image"

	managerCmd.Flags().StringVarP(&whitelistVolumes, "whitelist", "", "", "Whitelist volumes.")
	envs["VOLBACK_WHITELIST"] = "whitelist"

	managerCmd.Flags().StringVarP(&blacklistVolumes, "blacklist", "", "", "Blacklist volumes.")
	envs["VOLBACK_BLACKLIST"] = "blacklist"

	managerCmd.Flags().BoolVarP(&whitelistAnnotation, "whitelist.annotations", "", false, "Require pvc whitelist annotation")
	envs["VOLBACK_WHITELIST_ANNOTATION"] = "whitelist.annotations"

	volbackCmd.SetValuesFromEnv(envs, managerCmd.Flags())
	volbackCmd.RootCmd.AddCommand(managerCmd)
}
