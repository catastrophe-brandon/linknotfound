import logging

import click
from gevent.pywsgi import WSGIServer
from linknotfound.web import create_app
from linknotfound.phase import scanner, test_run_time

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
    test_run_time()


@cli.command(help="run scanner")
def scan():
    scanner()


@cli.command(help="run web application to list and access reports")
def web():
    web = create_app()
    http_server = WSGIServer(("0.0.0.0", 8000), web)
    http_server.serve_forever()


if __name__ == "__main__":
    cli()
