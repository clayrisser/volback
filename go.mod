module github.com/camptocamp/bivac

require (
	github.com/BurntSushi/toml v0.3.1
	github.com/Sirupsen/logrus v1.0.6
	github.com/codejamninja/volback v0.0.0-20190531035400-3af709696ed1
	github.com/docker/docker v0.0.0-20190121204153-8d7889e51013
	github.com/golang/mock v1.2.0
	github.com/gorilla/mux v1.6.2
	github.com/jinzhu/copier v0.0.0-20180308034124-7e38e58719c3
	github.com/prometheus/client_golang v0.9.2
	github.com/rancher/go-rancher v0.0.0-20190109212254-cbc1b0a3f68d
	github.com/rancher/go-rancher-metadata v0.0.0-20170929155856-d2103caca587
	github.com/spf13/cobra v0.0.3
	github.com/spf13/pflag v1.0.3
	github.com/spf13/viper v1.3.1
	github.com/stretchr/testify v1.3.0
	github.com/tatsushid/go-prettytable v0.0.0-20141013043238-ed2d14c29939
	golang.org/x/net v0.0.0-20190522155817-f3200d17e092
	gopkg.in/jarcoal/httpmock.v1 v1.0.0-20181117152235-275e9df93516
	k8s.io/api v0.0.0-20190126160303-ccdd560a045f
	k8s.io/apimachinery v0.0.0-20190126155707-0e6dcdd1b5ce
	k8s.io/client-go v0.0.0-20190126161006-6134db91200e
)

replace github.com/docker/docker => github.com/moby/moby v0.7.3-0.20190217132422-c093c1e08b60
