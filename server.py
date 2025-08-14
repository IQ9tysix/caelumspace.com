# server.py
import secrets
from flask import Flask

server = Flask(__name__)

# Safely set a secret key only once
server.secret_key = server.secret_key or secrets.token_hex(32)
