import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "ripley-demo-secret-key")

    # Por defecto usa SQLite para que el proyecto corra rápido en Visual Studio Code.
    # Para MySQL, cambiar DB_ENGINE=mysql y completar variables en .env.
    DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")

    if DB_ENGINE == "mysql":
        DB_USER = os.getenv("DB_USER", "root")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "3306")
        DB_NAME = os.getenv("DB_NAME", "sistema_reportes")
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///sistema_reportes.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
