from flask import Flask, jsonify

from logic import make_status


app = Flask(__name__)


@app.get("/")
def index():
    return "Jenkins CI/CD Demo - version 10"


@app.get("/health")
def health():
    return jsonify(make_status()), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
