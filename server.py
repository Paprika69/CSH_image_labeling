# -*- coding: utf-8 -*-
from app import app, db
from flask import Blueprint
# import controllers of the api module
from app.api.controllers.metadata import ns as metadata_namespace
# import controllers of the web module to render and display web page
from app.web.controllers.metadata import HomeView
from app.api.models.image import Image
from app.api.metadata import api


def initialize_app(flask_app):
    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(metadata_namespace)
    flask_app.register_blueprint(blueprint)
    db.register([Image])

    HomeView.register(flask_app)


def main():
    initialize_app(app)
    app.jinja_env.auto_reload = True
    app.run(debug=True)


if __name__ == "__main__":
    main()