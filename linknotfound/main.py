import logging

import click
import datetime
from gevent.pywsgi import WSGIServer
from linknotfound.phase import Runner
from linknotfound.web import create_app
from linknotfound.util import APP_NAME

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
)


@click.group()
def cli():
    pass


@cli.command(help="test program execution")
def test():
    logging.info(f"{APP_NAME} is fine!")
    exit(0)


@cli.command(help="run scanner")
def scan():
    start_time = datetime.datetime.now()
    logging.info(f"{APP_NAME} is running ...")
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
        f"scan completed report "
        f"saved at {runner.cfg.LNF_REPORT_PATH}/{runner.cfg.LNF_REPORT_NAME}"
    )
    print("\n\n")


@cli.command(help="run web application to list and access reports")
def web():
    web = create_app()
    http_server = WSGIServer(("0.0.0.0", 8000), web)
    http_server.serve_forever()


if __name__ == "__main__":
    cli()
