from datetime import datetime
from typing import List

from linknotfound.util import HTTP_STATUS_BROKEN_LINK
import json


class RPDocLink(object):
    """Report Doc links - 3rd level"""

    def __int__(self, file_name, url, status):
        self.file_name = file_name
        self.url = url
        self.status = status


class RPRepo(object):
    """Report Repositories - 2nd level"""

    def __int__(self, name, path, url, link, tf, tl, tbl):
        self.name = name
        self.path = path
        self.url = url
        self.link = link
        self.total_files = tf
        self.total_links = tl
        self.total_broken_links = tbl


class RPOrg(object):
    """Report Organization - 1st level"""

    def __int__(self, name, url, repos, tr, trf):
        self.name = name
        self.url = url
        self.repos = repos
        self.total_repos = tr
        self.total_repos_filtered = trf


def tweak_file_name(file_name: str, repo_name: str, local_path_prefix: str) -> str:
    """
    File names produced by the scanner include some artifacts of the scanning process, namely:
    1. Local file system path
    2. repository name
    The purpose of this function is to clean the file name in post-processing to avoid changing the scanning logic.
    """
    return (
        file_name.replace(local_path_prefix, "")
        .lstrip("/")
        .replace(repo_name, "")
        .lstrip("/")
    )


def dedupe(input_list: List):
    """
    There's probably a better way to do this but migraine meds prevent me from elucidation.
    """
    result = []
    files = []
    for item in input_list:
        if item["file"] not in files:
            result.append(item)
            files.append(item["file"])
    return result


class Report(object):
    """Report body"""

    report_date = datetime.today().strftime("%Y-%m-%d-%H%M")
    report_header = "-=-=-=" * 25
    duration = None
    org = RPOrg()

    def to_console(self):
        print(self.report_header)
        print(f"DATE: {self.report_date}")
        print(f"SCAN DURATION: {self.duration}")
        print(f"GH ORGANIZATION: {self.org.name}")
        print(f"TOTAL REPOS: {self.total_repos}")
        print(f"REPOS SCANNED: {self.total_repos_filtered}")
        for repo in self.org.repos:
            print(f"-" * 50)
            print(f"REPO NAME: {repo.name}")
            print(f"REPO URL: {repo.url}")
            print(f"FILES IN REPO: {repo.total_files}")
            print(f"FILES WITH DOC LINK:{repo.total_links}")
            print(f"TOTAL BROKEN LINK:{repo.total_broken_links}")
            count = 1
            for lk in repo.link:
                if lk.status in HTTP_STATUS_BROKEN_LINK:
                    print(f"\t{count}. FILE: {lk.file_name}")
                    print(f"\tURL: {lk.url}")
                    count += 1

    def to_file(self, report_path, report_name):
        with open(f"{report_path}{report_name}", "w") as report_file:
            report_file.write(f"DATE: {self.report_date}")
            report_file.write(f"\nSCAN DURATION: {self.duration}")
            report_file.write(f"\nGH ORGANIZATION: {self.org.name}")
            report_file.write(f"\nTOTAL REPOS: {self.total_repos}")
            report_file.write(f"\nREPOS SCANNED: {self.total_repos_filtered}")
            for repo in self.org.repos:
                report_file.write(f"\n")
                report_file.write(f"-" * 50)
                report_file.write(f"\nREPO NAME: {repo.name}")
                report_file.write(f"\nREPO URL: {repo.url}")
                report_file.write(f"\nFILES IN REPO: {repo.total_files}")
                report_file.write(f"\nFILES WITH DOC LINK:{repo.total_links}")
                report_file.write(f"\nTOTAL BROKEN LINK:{repo.total_broken_links}")
                count = 1
                for lk in repo.link:
                    if lk.status in HTTP_STATUS_BROKEN_LINK:
                        report_file.write(f"\n\t{count}. FILE: {lk.file_name}")
                        report_file.write(f"\n\tURL: {lk.url}")
                        count += 1

    def build_json(self, path_prefix_to_remove: str):
        """
        @param path_prefix_to_remove a string that can be removed from every file_name; needed
        because the scanner stores the absolute local file path in the data.
        """
        results = []
        for repo in self.org.repos:
            broken_links = [
                {
                    "file": tweak_file_name(
                        lk.file_name, repo.name, path_prefix_to_remove
                    ),
                    "url": lk.url,
                    "status_code": lk.status,
                }
                for lk in repo.link
                if lk.status in HTTP_STATUS_BROKEN_LINK
            ]
            results.append(
                {
                    "repo_name": repo.name,
                    "repo_url": repo.url,
                    "broken_links": dedupe(broken_links),
                }
            )
        return {"report": results, "report_date": datetime.now().isoformat()}

    def to_json(self, report_path, report_name, scan_path, filtered_repos):
        with open(f"{report_path}{report_name}", "w") as file:
            json.dump(self.build_json(scan_path), file, indent=4)
