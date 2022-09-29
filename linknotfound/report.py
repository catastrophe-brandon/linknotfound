from datetime import datetime
from linknotfound.util import HTTP_STATUS_BROKEN_LINK


class RPDocLink:
    """Report Doc links - 3rd level"""

    def __int__(self, file_name, url, status):
        self.file_name = file_name
        self.url = url
        self.status = status


class RPRepo:
    """Report Repositories - 2nd level"""

    def __int__(self, name, url, link, tf, tl, tbl):
        self.name = name
        self.url = url
        self.link = link
        self.total_files = tf
        self.total_links = tl
        self.total_broken_links = tbl


class RPOrg:
    """Report Organization - 1st level"""

    def __int__(self, name, url, repos, tr, trf):
        self.name = name
        self.url = url
        self.repos = repos
        self.total_repos = tr
        self.total_repos_filtered = trf


class Report:
    """Report body"""

    report_date = datetime.today().strftime("%Y-%m-%d")
    report_header = "-=-=-=" * 25
    duration = None
    org = RPOrg()

    def to_console(self):
        print(self.report_header)
        print(f"DATE: {self.report_date}")
        print(f"DURATION: {self.duration}")
        print(f"Organization: {self.org.name}")
        print(f"Total Repos: {self.total_repos}")
        print(f"Total Repos Filtered: {self.total_repos_filtered}")
        for repo in self.org.repos:
            print(f"-" * 50)
            print(f"REPO: {repo.name}")
            print(f"URL: {repo.url}")
            print(f"TOTAL FILES: {repo.total_files}")
            print(f"TOTAL DOC LINK:{repo.total_links}")
            print(f"TOTAL BROKEN LINK:{repo.total_broken_links}")
            count = 1
            for lk in repo.link:
                if lk.status in HTTP_STATUS_BROKEN_LINK:
                    print(f"\t{count}. FILE: {lk.file_name}")
                    print(f"\tURL: {lk.url}")
                    count += 1

    def to_file(self, report_path, report_name):
        with open(
            f"{report_path}/{self.report_date}-{report_name}.txt", "w"
        ) as report_file:
            report_file.write(f"DATE: {self.report_date}")
            report_file.write(f"\nDURATION: {self.duration}")
            report_file.write(f"\nOrganization: {self.org.name}")
            report_file.write(f"\nTotal Repos: {self.total_repos}")
            report_file.write(f"\nTotal Repos Filtered: {self.total_repos_filtered}")
            for repo in self.org.repos:
                report_file.write(f"\n")
                report_file.write(f"-" * 50)
                report_file.write(f"\nREPO: {repo.name}")
                report_file.write(f"\nURL: {repo.url}")
                report_file.write(f"\nTOTAL FILES: {repo.total_files}")
                report_file.write(f"\nTOTAL DOC LINK:{repo.total_links}")
                report_file.write(f"\nTOTAL BROKEN LINK:{repo.total_broken_links}")
                count = 1
                for lk in repo.link:
                    if lk.status in HTTP_STATUS_BROKEN_LINK:
                        report_file.write(f"\n\t{count}. FILE: {lk.file_name}")
                        report_file.write(f"\n\tURL: {lk.url}")
                        count += 1
