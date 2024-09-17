from flask import Flask, render_template
from src.web.handlers import error
from src.web.config import config
from src.web.controllers.user_controller import bp as user_bp
from src.model import database
from src.model.config import config
from src.model import seeds

def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)
    
    app.config.from_object(config[env])
    database.init_app(app)
    
    @app.route("/")
    def home():
        return render_template('home.html')
    
    app.register_blueprint(user_bp)

    app.register_error_handler(404, error.error_not_found)
    
    @app.cli.command(name="reset-db")
    def reset_db():
        database.reset()

    @app.cli.command("seed-db")
    def seed_db():
        seeds.run()
        print("Base de datos sembrada")

    return app
