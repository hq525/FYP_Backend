from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from db import db

app = Flask(__name__)
app.config.from_object("config.Config")
api = Api(app)

@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWTManager(app)

# @jwt.user_claims_loader
# def add_claims_to_jwt(identity):  
#     if identity == 1:   
#         return {'is_admin': True}
#     return {'is_admin': False}

# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
# @jwt.token_in_blacklist_loader
# def check_if_token_in_blacklist(decrypted_token):
#     return decrypted_token['jti'] in BLACKLIST  # Here we blacklist particular JWTs that have been created in the past.

@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'message': 'The token has expired.',
        'error': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):  
    return jsonify({
        'message': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'error': 'authorization_required'
    }), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        "description": "The token is not fresh.",
        'error': 'fresh_token_required'
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        "description": "The token has been revoked.",
        'error': 'token_revoked'
    }), 401

if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)