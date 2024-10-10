from flask import Flask
from engine.resources_handler import ResourcesHandler
from engine.compatibility_core import CompatibilityCore

def create_app():
    app = Flask(__name__, template_folder='app/temp', static_folder='app/static')

    resources_handler = ResourcesHandler() # Создание экземпляра ResourcesHandler

    compatibility_core = CompatibilityCore() # Создание экземпляра CompatibilityCore

    return app, resources_handler, compatibility_core
