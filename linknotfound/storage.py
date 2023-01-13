import logging
import boto3
import boto3.session
from boto3.session import Session

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
)


class CustomSession(Session):
    def __new__(cls, cfg):
        if not hasattr(cls, "instance"):
            cls.instance = Session(
                aws_access_key_id=cfg.LNF_AWS_ACCESS_KEY_ID,
                aws_secret_access_key=cfg.LNF_AWS_SECRET_ACCESS_KEY,
            )
        return cls.instance


def upload_file(file_name, cfg):
    object_name = file_name
    # TODO: update this code to use session object
    s3_client = boto3.client("s3")
    response = s3_client.upload_file(file_name, cfg.LNF_S3_BUCKET, object_name)
    return response


def download_file(file_name, cfg):
    session = CustomSession(cfg)
    s3 = session.resource("s3")
    output = f"downloads/{file_name}"
    s3.Bucket(cfg.LNF_S3_BUCKET).download_file(file_name, output)
    return output


def get_file(file_name, cfg):
    session = CustomSession(cfg)
    s3 = session.resource("s3")
    file_content = s3.Bucket(cfg.LNF_S3_BUCKET).Object(file_name).get()
    data = file_content["Body"].read().decode("utf-8")
    return data


def list_files(cfg):
    session = CustomSession(cfg)
    s3 = session.resource("s3")

    bucket_obj = s3.Bucket(cfg.LNF_S3_BUCKET)
    contents = []
    for report in bucket_obj.objects.all():
        contents.append(report)
    return contents
