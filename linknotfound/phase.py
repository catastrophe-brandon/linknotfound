import logging
import os

import re
import sys
from shutil import rmtree

import requests
from os import getenv, environ, path, mkdir, walk
from linknotfound.util import get_config, get_links_sum
from linknotfound import app_name
from linknotfound.report import Report, RPRepo, RPDocLink
from github import Github
from git import Repo

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


class LnfCfg:
    """
    Default configuration to run the program.

    Load the program configurations specified in linknotfound.conf file.
    The configuration also can be declared by environment variables, when set the environment variables
    have high priority during the load, skipping loading the configurations from the file.
    To set as environment variable, the variable name must start
    with LNF_ and following the section and the configuration key and value as example:

        in linknotfound.conf:

        [github]
        organization = "*********"
        token = "**********"

        as environment variables:

        LNF_GITHUB_ORGANIZATION="*********"
        LNF_GITHUB_TOKEN="**********"

    """

    LNF_GITHUB_ORGANIZATION = None
    LNF_GITHUB_TOKEN = None
    LNF_REPOS_CONTAINS = ["-ui", "-frontend"]
    LNF_SCAN_PATH = "/var/tmp/linknotfound"
    LNF_SCAN_EXCLUDE = [".git", ".travis"]
    LNF_SCAN_REGEX = None
    LNF_REPORT_NAME = "linknotfound"
    LNF_REPORT_PATH = "/var/tmp/"

    @staticmethod
    def load_configuration():
        logging.info(f"loading configuration")
        _cfg = LnfCfg()

        if path.exists(f"{app_name}.conf"):
            logging.info(f"loading configuration from file {app_name}.conf")

            # linknotfound.conf GitHub
            _config_github = "github"
            _cfg.LNF_GITHUB_ORGANIZATION = get_config(_config_github, "organization")
            _cfg.LNF_GITHUB_TOKEN = get_config(_config_github, "token") or getenv(
                "GITHUB_TOKEN"
            )

            # linknotfound.conf repos
            _config_repos = "repos"
            _cfg.LNF_REPOS_CONTAINS = get_config(_config_repos, "contains")

            # linknotfound.conf scan
            _config_scan = "scan"
            _cfg.LNF_SCAN_PATH = get_config(_config_scan, "path")
            _cfg.LNF_SCAN_EXCLUDE = get_config(_config_scan, "exclude")
            _cfg.LNF_SCAN_REGEX = get_config(_config_scan, "regex")

            # linknotfound.conf report
            _config_report = "report"
            _cfg.LNF_REPORT_NAME = get_config(_config_report, "name")
            _cfg.LNF_REPORT_PATH = get_config(_config_report, "path")

        for k in [a for a in dir(_cfg) if a.startswith("LNF_")]:
            if k in os.environ:
                logging.info(f"overriding configuration {k}")
                setattr(_cfg, k, os.getenv(k))

        return _cfg


class Runner:
    cfg = None
    gh = None
    rp = None

    def runner_init(self):
        self.cfg = LnfCfg().load_configuration()
        logging.info(f"CFG filtering repos: {self.cfg.LNF_REPOS_CONTAINS}")
        logging.info(f"CFG scan path: {self.cfg.LNF_SCAN_PATH}")
        logging.info(f"CFG report path: {self.cfg.LNF_REPORT_PATH}")

        self.rp = Report()

        try:
            if not self.cfg.LNF_GITHUB_TOKEN:
                raise RuntimeError
        except RuntimeError:
            logging.error(
                f"Missing github TOKEN, check GITHUB_TOKEN or LNF_GITHUB_TOKEN env var or token in {app_name}.conf"
            )
            sys.exit(1)

        environ["GITHUB_TOKEN"] = self.cfg.LNF_GITHUB_TOKEN
        self.gh = Github(login_or_token=f"{self.cfg.LNF_GITHUB_TOKEN}")

        if path.exists(self.cfg.LNF_SCAN_PATH):
            rmtree(self.cfg.LNF_SCAN_PATH)
        if not path.exists(self.cfg.LNF_SCAN_PATH):
            mkdir(self.cfg.LNF_SCAN_PATH)

    def get_org_repos(self) -> [Repo]:
        """
        Get GitHub organization object from organization specified in config file
        :return: [Repo]
        """
        org = self.gh.get_organization(self.cfg.LNF_GITHUB_ORGANIZATION)
        repos = org.get_repos()
        self.rp.org.name = self.cfg.LNF_GITHUB_ORGANIZATION
        self.rp.total_repos = repos.totalCount
        return repos

    def filter_repos(self, repos) -> [Repo]:
        """
        Filter GitHub organization repositories based on contains string from config file
        :param repos: list of repositories object
        :return: list of filtered repositories object
        """
        l_filtered = []
        for repo in repos:
            if any(st in f"{repo.name}" for st in self.cfg.LNF_REPOS_CONTAINS):
                l_filtered.append(repo)
        self.rp.total_repos_filtered = l_filtered.__len__()
        return l_filtered

    def scan(self, repos):
        """
        scan files
        :param repos: List of Repo objects
        :return: Report object
        """
        # RPRepo
        rp = []
        for repo in repos:
            rp_repo = RPRepo()
            rp_repo.name = repo.name
            rp_repo.url = repo.html_url

            logging.info(f"cloning {repo.full_name}")
            Repo.clone_from(
                url=f"https://{self.cfg.LNF_GITHUB_TOKEN}@github.com/{repo.full_name}.git",
                to_path=f"{self.cfg.LNF_SCAN_PATH}/{repo.name}",
            )

            # repo files
            l_files = []
            for curr_path, currentDirectory, files in walk(
                f"{self.cfg.LNF_SCAN_PATH}/{repo.name}"
            ):
                for file in files:
                    file_abs = path.join(curr_path, file)
                    if any(st in f"{file_abs}" for st in self.cfg.LNF_SCAN_EXCLUDE):
                        break
                    l_files.append(file_abs)

            rp_repo.total_files = l_files.__len__()
            logging.info(f"total files: {l_files.__len__()}")

            # find DocLink in file
            lk = []
            for f_name in l_files:
                # read file content, search for docs url
                try:
                    with open(f_name, "r") as fp:
                        data = fp.read()
                        matches = re.finditer(
                            self.cfg.LNF_SCAN_REGEX, data, re.IGNORECASE
                        )
                        # doc url present in file
                        for match in matches:
                            rp_doc = RPDocLink()
                            rp_doc.file_name = f_name
                            rp_doc.url = str(match[0]).replace("'", "")
                            # check doc url is accessible
                            rp_doc.status = requests.get(url=rp_doc.url).status_code
                            lk.append(rp_doc)
                            logging.info(f"{rp_doc.status}\n\t{rp_doc.file_name}")
                except UnicodeError:
                    pass
            rp_repo.link = lk
            rp_repo.total_broken_links, rp_repo.total_links = get_links_sum(lk)
            rp.append(rp_repo)
        self.rp.org.repos = rp
