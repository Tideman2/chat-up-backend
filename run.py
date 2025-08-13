from myapp.app import create_app, db
from user.user_route import auth_bp

app = create_app()

print(app.blueprints)

if not app.blueprints.get("auth"):
    app.register_blueprint(auth_bp)

print(app.blueprints)


@app.route('/')
def home():
    return "Backend is running!"


with app.app_context():
    db.create_all()

if __name__ == "__main__":

    app.run(debug=True)
