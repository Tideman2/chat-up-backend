# tests/models_test.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that models can be imported"""
    try:
        # Import your app first to set up everything
        from myapp.app import create_app
        app = create_app()

        with app.app_context():
            from models.notifications_model import MessageNotificationModel
            from models.user_model import User

            print("✅ All imports successful!")
            return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


if __name__ == "__main__":
    test_imports()
