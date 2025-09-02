from myapp.app import create_app, db
from routes.auth_route import auth_bp
from routes.user_route import user_bp

app = create_app()

print(app.blueprints)

if not app.blueprints.get("auth"):
    app.register_blueprint(auth_bp)

if not app.blueprints.get("user"):
    app.register_blueprint(user_bp)

print(app.blueprints)

if __name__ == "__main__":

    app.run(debug=True)
