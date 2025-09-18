from fastapi import FastAPI

app: FastAPI = None

def get_app() -> FastAPI:
    if app is None:
        raise RuntimeError("App has not been set.")
    return app

def set_app(application: FastAPI):
    global app
    app = application
