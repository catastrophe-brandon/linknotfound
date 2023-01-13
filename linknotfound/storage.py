import logging
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


def upload_file(report_file_name, runner):
    session = CustomSession(runner.cfg)
    s3 = session.resource("s3")
    with open(f"{runner.cfg.LNF_REPORT_PATH}{report_file_name}", "rb") as data:
        s3.Object(runner.cfg.LNF_S3_BUCKET, report_file_name).put(
            Body=data, Metadata=runner.metadata
        )


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
    metadata = file_content["Metadata"]
    obj_file = {"data": data, "metadata": metadata}
    return obj_file


def list_files(cfg):
    session = CustomSession(cfg)
    s3 = session.resource("s3")
    bucket_obj = s3.Bucket(cfg.LNF_S3_BUCKET)
    contents = []
    for report in bucket_obj.objects.all():
        contents.append(report)
    return contents
