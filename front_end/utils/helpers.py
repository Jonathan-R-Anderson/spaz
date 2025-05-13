import os
import random
import ipaddress
from pathlib import Path
from flask import Flask
from flask_restful import Api
from werkzeug.datastructures import ImmutableDict
from web3 import Web3
from web3.exceptions import ContractLogicError
import json
import logging
import threading
import subprocess
import time
import docker
import hmac
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import json, os, logging, hmac, hashlib, base64, requests, subprocess
from werkzeug.utils import secure_filename
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from flask import Blueprint, render_template, request, jsonify, send_from_directory





class ManiwaniApp(Flask):
    jinja_options = ImmutableDict()

app.config['TEMPLATES_AUTO_RELOAD'] = os.getenv('TEMPLATES_AUTO_RELOAD', True)
blueprint = Blueprint('blueprint', __name__)



app.url_map.strict_slashes = False


