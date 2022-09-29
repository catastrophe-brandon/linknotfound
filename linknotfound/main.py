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
    repos = runner.get_org_repos()
    filtered_repos = runner.filter_repos(repos)
    runner.scan(filtered_repos)
    end_time = datetime.datetime.now()
    runner.rp.duration = end_time - start_time
    runner.rp.to_console()
    runner.rp.to_file(
        report_path=runner.cfg.report_path, report_name=runner.cfg.report_name
    )


@click.command()
@click.option("--test", is_flag=True, help="testing app")
def cli(test):
    if test:
        click.echo(f"{app_name} is fine!")
        exit(0)
    run()


if __name__ == "__main__":
    cli()
