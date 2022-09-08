from datetime import datetime


class RPDocLink:
    file_name = None
    url = None
    status = None


class RPRepo:
    repo_name = None
    total_files = 0
    total_doc_url_found = 0
    total_doc_broken_link = 0
    doc_link = [RPDocLink]


class RPOrg:
    org_name = None
    total_repos = 0
    total_repos_filtered = 0
    repos = [RPRepo]


class Report(RPOrg):
    report_date = datetime.today().strftime("%Y-%m-%d")
    report_header = "-=-=-=-=-=-=-=-="

    def gen(self):
        return f" {self.report_date} {self.org_name} {self.total_repos} {self.total_repos_filtered}"
