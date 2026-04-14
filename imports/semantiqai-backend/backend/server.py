from backend.platform.app_factory import create_app
from backend.platform.config import Settings

app = create_app()

if __name__ == "__main__":
    app.run(
        host=Settings.HOST,
        port=Settings.PORT,
        debug=Settings.DEBUG
    )
