import os

os.environ.setdefault("FASTAPI_SETTINGS_MODULE", 'example.settings')
from example.factory import create_app

app = create_app()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, debug=True, port=8000, lifespan="on")
