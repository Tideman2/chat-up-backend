from myapp import app


@app.route("/")
def home():
    return "Hello from Flask with __init__.py!"
