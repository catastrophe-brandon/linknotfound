import logging

import click
from linknotfound import app_name
from linknotfound.phase import Runner
import datetime

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


def run():
    start_time = datetime.datetime.now()
    logging.info(f"{app_name} is running ...")
    runner = Runner()
    runner.runner_init()
    repos = runner.get_org_repos()
    filtered_repos = runner.filter_repos(repos)
    runner.scan(filtered_repos)
    end_time = datetime.datetime.now()
    runner.rp.duration = end_time - start_time
    runner.rp.to_console()
    runner.rp.to_file(
        report_path=runner.cfg.LNF_REPORT_PATH, report_name=runner.cfg.LNF_REPORT_NAME
    )
    print("\n\n")
    logging.info(
        f"scan completed! report saved at {runner.cfg.LNF_REPORT_PATH}/{runner.cfg.LNF_REPORT_NAME}"
    )
    print("\n\n")


@click.command()
@click.option("--test", is_flag=True, help="testing app")
@click.option("--scan", is_flag=True, help="run scanner")
def cli(test, scan):
    if test:
        logging.info(f"{app_name} is fine!")
        exit(0)
    if scan:
        run()


if __name__ == "__main__":
    cli()
