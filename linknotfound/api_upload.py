import logging
import requests

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
)


def upload_json_file(file_name):
    """
    Upload a JSON "report" of broken links to the API via POST.
    """
    logging.info("=== Uploading Scan Results to API ===")
    # TODO: Implement me once the API exists
    pass
