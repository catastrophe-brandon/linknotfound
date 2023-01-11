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

# Contributing and running the application

## Requirements
* GitHub OauthAPI GITHUB_TOKEN
* Python 3

## Development environment

From the path ./linknotfound run the script below to set developer environment for this program in a consistent way:

```shell
sh ops/scripts/set_dev_env.sh
```

Or if you prefer to set it manually, from the path ./linknotfound run the command below:

```shell
pip install --editable .[dev]
```

### configuration

This program requires some configuration to be in the file **linknotfound/linknotfound.conf**. You
can use the template file [linknotfound/linknotfound.conf.sample](../linknotfound/linknotfound.conf.sample) for
creating your own file then update it with your credentials before running the program.

### running

If running the program from your local development environment, use the path ./linknotfound/linknotfound as the root
before running the commands below. If running in container, you must be in the path ./linknotfound

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

Any PR is welcome and will pass through the code-review process. Be responsive with the code organization and run
lint from the path ./linknotfound before your contributions:

```shell
pre-commit run --all
```

## links
* [GitPython](https://github.com/gitpython-developers/GitPython)
* [tips python git repo](https://www.devdungeon.com/content/working-git-repositories-python)

<br><br><br>
[<img src="docs/img/pnf.jpg" width="250"/>](logo)<br>
_Life is too short to be serious all the time! So, if you can't laugh at yourself, call me... I'll laugh with you._
