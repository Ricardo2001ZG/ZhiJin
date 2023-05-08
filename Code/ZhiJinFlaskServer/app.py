#!/usr/bin/env python3
import os
from flask import Flask
from lib_app.models import db
from lib_app.routes import routes

def create_app():
    app = Flask(__name__)
    # Load configuration from external source here
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['JSON_AS_ASCII'] = False
    app.register_blueprint(routes)

    # Bind db to app
    db.init_app(app)

    # Create database tables
    with app.app_context():
        db.drop_all()
        db.create_all()

    for rule in app.url_map.iter_rules():
        print(rule, rule.methods)
    return app

if __name__ == '__main__':
    app = create_app()
    debug_mode = os.getenv("FLASK_DEBUG") == "True"
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(debug=debug_mode, port=port)
