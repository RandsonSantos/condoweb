import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/condominio")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-change-me")
    ESP32_BASE_URL = os.environ.get("ESP32_BASE_URL", "http://192.168.0.120")
    ESP32_TOKEN = os.environ.get("ESP32_TOKEN", "")
    HLS_OUTPUT_DIR = os.environ.get("HLS_OUTPUT_DIR", "/var/www/html/streams")
