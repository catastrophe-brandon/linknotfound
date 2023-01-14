import logging
from flask import Flask, render_template, request, send_file
from linknotfound.storage import list_files, download_file, get_file
from linknotfound.util import LnfCfg

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
)


def create_app():
    app = Flask(__name__)
    cfg = LnfCfg()

    @app.route("/")
    def home():
        files_in_bucket = list_files(cfg)
        contents = []
        for item in files_in_bucket:
            contents.append(item.key)
        content_sorted = sorted(contents, reverse=True)
        return render_template("home.html", contents=content_sorted)

    @app.route("/how")
    def how():
        return render_template("how.html")

    @app.route("/get/<filename>", methods=["GET"])
    def get(filename):
        if request.method == "GET":
            obj_file = get_file(filename, cfg)
            data = obj_file["data"]
            metadata = obj_file["metadata"]
            return render_template(
                "report.html", data=data, metadata=metadata, title=filename
            )

    @app.route("/download/<filename>", methods=["GET"])
    def download(filename):
        if request.method == "GET":
            output = download_file(filename, cfg)
            return send_file(output, as_attachment=True)

    return app
