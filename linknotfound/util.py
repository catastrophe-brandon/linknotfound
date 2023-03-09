import logging
import json
import re
from configparser import SafeConfigParser
from datetime import datetime, timedelta
from os import remove, rename, listdir, path, getenv, environ
from subprocess import call, check_output

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
)

APP_NAME = "linknotfound"
HTTP_STATUS_BROKEN_LINK = [400, 403, 404]
HTTP_STATUS_WORKING_LINK = [200, 202]
HTTP_STATUS_RETRY_FORCE = [429, 500, 502, 503, 504]
HTTP_METHOD_WHITELIST = ["HEAD", "GET", "OPTIONS"]


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

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(LnfCfg, cls).__new__(cls)
            cls.instance.load_configuration()
        return cls.instance

    # DEFAULT values
    # GitHub
    LNF_GITHUB_ORGANIZATION = None
    LNF_GITHUB_TOKEN = None
    LNF_REPOS_CONTAINS = ["-ui", "-frontend"]
    # Scanner
    LNF_SCAN_PATH = "/var/tmp/linknotfound"
    LNF_SCAN_EXCLUDE = [".git", ".travis"]
    LNF_SCAN_REGEX = None
    # Report
    LNF_REPORT_NAME = "linknotfound"
    LNF_REPORT_PATH = "/var/tmp/"
    # AWS
    LNF_S3_BUCKET = "report-linknotfound"
    LNF_AWS_ACCESS_KEY_ID = None
    LNF_AWS_SECRET_ACCESS_KEY = None

    def load_configuration(self):
        _config_path = getenv("CONFIG", "linknotfound.conf")
        if path.exists(f"{_config_path}"):
            logging.info(f"loading configuration from file {_config_path}")

            # linknotfound.conf GitHub
            _config_github = "github"
            self.LNF_GITHUB_ORGANIZATION = get_config(
                _config_path,
                _config_github,
                "organization",
                self.LNF_GITHUB_ORGANIZATION,
            )
            self.LNF_GITHUB_TOKEN = get_config(
                _config_path, _config_github, "token", self.LNF_GITHUB_TOKEN
            ) or getenv("GITHUB_TOKEN")

            # linknotfound.conf repos
            _config_repos = "repos"
            self.LNF_REPOS_CONTAINS = get_config(
                _config_path, _config_repos, "contains", self.LNF_REPOS_CONTAINS
            )

            # linknotfound.conf scan
            _config_scan = "scan"
            self.LNF_SCAN_PATH = get_config(
                _config_path, _config_scan, "path", self.LNF_SCAN_PATH
            )
            self.LNF_SCAN_EXCLUDE = get_config(
                _config_path, _config_scan, "exclude", self.LNF_SCAN_EXCLUDE
            )
            self.LNF_SCAN_REGEX = get_config(
                _config_path, _config_scan, "regex", self.LNF_SCAN_REGEX
            )

            # linknotfound.conf report
            _config_report = "report"
            self.LNF_REPORT_NAME = get_config(
                _config_path, _config_report, "name", self.LNF_REPORT_NAME
            )
            self.LNF_REPORT_PATH = get_config(
                _config_path, _config_report, "path", self.LNF_REPORT_PATH
            )

            # linknotfound.conf aws
            _config_report = "aws"
            self.LNF_S3_BUCKET = get_config(
                _config_path, _config_report, "bucket", self.LNF_S3_BUCKET
            )
            self.LNF_AWS_ACCESS_KEY_ID = get_config(
                _config_path,
                _config_report,
                "aws_access_key_id",
                self.LNF_AWS_ACCESS_KEY_ID,
            )
            self.LNF_AWS_SECRET_ACCESS_KEY = get_config(
                _config_path,
                _config_report,
                "aws_secret_key_id",
                self.LNF_AWS_SECRET_ACCESS_KEY,
            )

        for k in [a for a in dir(self.instance) if a.startswith("LNF_")]:
            if k in environ:
                logging.info(f"overriding configuration {k}")
                setattr(self.instance, k, getenv(k))

        return self.instance

    @staticmethod
    def get_cfg():
        cfg = LnfCfg()
        return cfg


def get_config(config_path, section, parameter, default):
    config = SafeConfigParser()
    config.read(config_path)

    if section not in config:
        return default

    # Updated because json.loads chokes on regex (and I'm not sure why it was done this way to begin with)
    if parameter == "regex":
        return config.get(section, parameter).strip('"')
    else:
        return json.loads(config.get(section, parameter))


def prepend_line(file_name, line):
    dummy_file = file_name + ".bak"
    with open(file_name, "r") as read_obj, open(dummy_file, "w") as write_obj:
        write_obj.write(line + "\n")
        for line in read_obj:
            write_obj.write(line)
    remove(file_name)
    rename(dummy_file, file_name)


def git_status(now):
    rs = check_output(["git", "status"], universal_newlines=True)
    line = "-" * 80
    report_header = f"{line}\n " f"{now}\n" f"{line}\n "
    prepend_line("report.txt", f"{report_header} {rs}")


def git_push():
    now = datetime.now()
    git_status(now)
    commit_message = f"{now} new snippets"
    call("git add .", shell=True)
    call('git commit -m "' + commit_message + '"', shell=True)
    call("git push origin main", shell=True)


def purge():
    day = get_config("purge", "day")
    files = listdir("snippet")
    for file in files:
        with open(f"snippet/{file}", "r") as fp:
            data = fp.read()
            dt = datetime.today() - timedelta(days=day)
            if dt.strftime("%Y-%m-%d") in data:
                remove(f"snippet/{file}")


def build_regex():
    """
    build regex from obfuscate_rules
    :return: str with regex for capturing sensitive data
    """

    rules_content = get_config("obfuscate_rules", "content")
    rules_content_size = len(rules_content)

    re_pattern = []
    re_open = "(.*"
    re_close = ".*)"
    re_join = "|"

    for item in rules_content:
        index = rules_content.index(item)
        if index == rules_content_size - 1:
            re_join = ""
        re_pattern.append(f"{re_open}{item}{re_close}{re_join}")

    return "".join(re_pattern)


def obfuscate():
    rules_separator = get_config("obfuscate_rules", "separator")
    rules_mask = get_config("obfuscate_rules", "mask")
    re_pattern = build_regex()

    files = listdir("snippet")
    for file in files:
        with open(f"snippet/{file}", "r+") as fp:
            data = fp.read()
            sensitive_data = re.finditer(re_pattern, data, re.IGNORECASE)
            to_replace = {}
            for match_obj in sensitive_data:
                # extract separator from seeker.conf obfuscate_rules
                for separator in rules_separator:
                    if separator in match_obj.group():
                        sensitive_cred_key = match_obj.group().split(separator)[0]
                        sensitive_cred_value = match_obj.group().split(separator)[1]
                        before = match_obj.group()

                        logging.info(
                            f"Found sensitive data in {file} on {sensitive_cred_key}"
                        )

                        if sensitive_cred_value.replace('"', "").strip() == rules_mask:
                            logging.info(
                                f"secret {sensitive_cred_key} is already masked"
                            )
                            break

                        after = before.replace(sensitive_cred_value, f' "{rules_mask}"')
                        to_replace[before] = after
                        break

            if len(to_replace) > 0:
                fp.seek(0)

                for k, v in to_replace.items():
                    data = data.replace(k, v)

                fp.write(data)


def get_links_sum(links):
    """
    Find broken and working links from a list of links
    HTTP STATUS CODE: https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml
    :param links: List of Repos
    :return: integer broken_links and working_links
    """
    broken_links = sum(1 for i in links if i.status in HTTP_STATUS_BROKEN_LINK)
    working_links = sum(1 for i in links if i.status in HTTP_STATUS_WORKING_LINK)
    return broken_links, working_links
