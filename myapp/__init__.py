from flask import Flask

app = Flask(__name__)


def register_routes():
    from myapp import routes  # imported only when this function runs


register_routes()
