# linknotfound

This project is a POC, [proof of concept](https://en.wikipedia.org/wiki/Proof_of_concept) for a simple tool to find and
report broken links from an application source code.

_This repository doesn't intend to be a final version of this poc, as well should not run in a production
environment, as a public and open-source code you can use it with your own risks and contributions are welcome!._

## diagrams

![diagram](docs/img/diagram.png)<br>
_high-level overview with configuration, execution and reporting_

![diagram](docs/img/linknotfound-GH-workflow-automation.png)<br>
_automation using GitHub workflow, triggered by new PR event_

## Requirements
* GitHub OauthAPI GITHUB_TOKEN
* Python 3

## Setup dev env

run the script below to set developer env for this program in a consistent way:

```shell
sh ops/scripts/set_dev_env.sh
```

Or manually:

```shell
pip install --editable .[dev]
```

before running, **linknotfound/linknotfound.conf** create from
sample [linknotfound/linknotfound.conf.sample](../linknotfound/linknotfound.conf.sample)

```shell
# checking installation
linknotfound --test

# running for real
linknotfound

# running in container
sh ops/scripts/docker_build.sh
sh ops/scripts/docker_run.sh
```

## contributing

before commit any code, run lint as showing below:

```shell
pre-commit run --all
```

## links
* [GitPython](https://github.com/gitpython-developers/GitPython)
* [tips python git repo](https://www.devdungeon.com/content/working-git-repositories-python)

<br><br><br>
[<img src="docs/img/pnf.jpg" width="250"/>](logo)<br>
_Life is too short to be serious all the time! So, if you can't laugh at yourself, call me... I'll laugh with you._
