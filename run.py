from myapp.app import create_app, db
from routes.auth_route import auth_bp
from routes.user_route import user_bp
from routes.notifications_route import notification_bp
from myapp.app import socketio

app = create_app()

if not app.blueprints.get("auth"):
    app.register_blueprint(auth_bp)

if not app.blueprints.get("user"):
    app.register_blueprint(user_bp)

if not app.blueprints.get("notification"):
    app.register_blueprint(notification_bp)

with app.app_context():
    db.create_all()
    print("✅ All missing tables created!")


@socketio.on("connect")
def handle_connect():
    print("A client just connected!")

# Fires whenever a client disconnects


@socketio.on("disconnect")
def handle_disconnect():
    print("A client just disconnected!")


if __name__ == "__main__":
    socketio.run(app=app)
