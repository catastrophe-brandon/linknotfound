import logging

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


class CfgLoader:
    # linknotfound.conf GitHub
    _config_github = "github"
    gh_org = get_config(_config_github, "organization")
    gh_token = get_config(_config_github, "token") or getenv("GITHUB_TOKEN")

    # linknotfound.conf repos
    _config_repos = "repos"
    repo_contains = get_config(_config_repos, "contains")

    # linknotfound.conf scan
    _config_scan = "scan"
    scan_path = get_config(_config_scan, "path")
    scan_exclude = get_config(_config_scan, "exclude")
    scan_regex = get_config(_config_scan, "regex")

    # linknotfound.conf report
    _config_report = "report"
    report_name = get_config(_config_report, "name")
    report_path = get_config(_config_report, "path")


class Planner:
    cfg = CfgLoader()
    logging.info(f"CFG repos contains: {cfg.repo_contains}")
    logging.info(f"CFG scan path: {cfg.scan_path}")
    logging.info(f"CFG report path: {cfg.report_path}")

    try:
        if not cfg.gh_token:
            raise RuntimeError
    except RuntimeError:
        logging.error(
            f"Missing github TOKEN, check GITHUB_TOKEN env var or token in {app_name}.conf"
        )
        sys.exit(1)

    environ["GITHUB_TOKEN"] = cfg.gh_token
    gh = Github(login_or_token=f"{cfg.gh_token}")

    if path.exists(cfg.scan_path):
        rmtree(cfg.scan_path)
    if not path.exists(cfg.scan_path):
        mkdir(cfg.scan_path)


class Runner(Planner):
    rp = Report()

    def get_org_repos(self) -> [Repo]:
        """
        Get GitHub organization object from organization specified in config file
        :return: [Repo]
        """
        org = self.gh.get_organization(self.cfg.gh_org)
        repos = org.get_repos()
        self.rp.org.name = self.cfg.gh_org
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
            if any(st in f"{repo.name}" for st in self.cfg.repo_contains):
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
                url=f"https://{self.cfg.gh_token}@github.com/{repo.full_name}.git",
                to_path=f"{self.cfg.scan_path}/{repo.name}",
            )

            # repo files
            l_files = []
            for curr_path, currentDirectory, files in walk(
                f"{self.cfg.scan_path}/{repo.name}"
            ):
                for file in files:
                    file_abs = path.join(curr_path, file)
                    if any(st in f"{file_abs}" for st in self.cfg.scan_exclude):
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
                        matches = re.finditer(self.cfg.scan_regex, data, re.IGNORECASE)
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
