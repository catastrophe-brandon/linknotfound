import logging
import click
from linknotfound import app_name
from linknotfound.phase import Runner

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


def run():
    logging.info(f"{app_name} is running ...")
    x = Runner()
    repos = x.get_org_repos()
    filtered_repos = x.filter_repos(repos)
    x.scan(filtered_repos)
    logging.info(x.rp.gen())


@click.command()
@click.option("--test", is_flag=True, help="testing app")
def cli(test):
    if test:
        click.echo(f"{app_name} is fine!")
        exit(0)
    run()


if __name__ == "__main__":
    cli()
