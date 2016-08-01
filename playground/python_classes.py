class Config:
    HOST = "0.0.0.0"
    PORT = 5001

class DevConfig(Config):
    HOST = "127.0.0.1"
    DEBUG = True

