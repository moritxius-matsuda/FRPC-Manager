from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'frpc-manager-secret-key'
    
    from .views import main
    app.register_blueprint(main)
    
    return app