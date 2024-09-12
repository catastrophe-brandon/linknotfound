import json
import logging
import requests

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
)


class UploadError(Exception):
    pass


def upload_json_file(abs_json_path: str, post_url: str):
    """
    Upload a JSON "report" of broken links to the API via POST.
    """
    logging.info("=== Uploading Scan Results to API ===")
    headers = {"Content-Type": "application/json"}
    with open(abs_json_path, "r") as json_file:
        response = requests.post(post_url, json=json.load(json_file), headers=headers)
        if response.status_code not in [200, 201]:
            logging.error(
                f"Response from POST to {post_url} was {response.status_code}"
            )
            raise UploadError
