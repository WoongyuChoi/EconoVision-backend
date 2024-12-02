import time

from flask import Flask, jsonify, request
from flask_caching import Cache

from api import check_ecos, fetch_exchange_rate
from config import Config
from handler.exception_handler import register_exception_handlers
from handler.logger import get_logger

app = Flask(__name__)
app.config.from_object(Config)

cache = Cache(app)
logger = get_logger(__name__)

register_exception_handlers(app)


@app.route("/")
def health_check():
    app.logger.info("Health check called.")
    status = {
        "status": "UP",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "details": {"ecos_api": "UP" if check_ecos() else "DOWN"},
    }
    return jsonify(status), 200


@app.route("/favicon.<ext>")
def favicon(ext):
    app.logger.debug(f"Favicon request received with extension: {ext}")
    return "", 204, {"Content-Type": "image/x-icon"}


@app.route("/api/exchange-rate", methods=["GET"])
@cache.cached(query_string=True)
def get_exchange_rate():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    item_code = request.args.get("item_code")

    data = fetch_exchange_rate(
        start_date=start_date, end_date=end_date, item_code=item_code
    )
    app.logger.info("Exchange rate data fetched successfully.")
    return jsonify(data), 200


def handler(event, context):
    from werkzeug.wrappers import Request, Response

    request = Request(event)
    response = Response.from_app(app, request.environ)

    return {
        "statusCode": response.status_code,
        "headers": dict(response.headers),
        "body": response.get_data(as_text=True),
    }
