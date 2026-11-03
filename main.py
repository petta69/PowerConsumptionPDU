import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    image_path = "static/powerchart.png"
    
    # Get the last modified timestamp of the image (defaults to 0 if file doesn't exist yet)
    image_v = int(os.path.getmtime(image_path)) if os.path.exists(image_path) else 0

    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "image_version": image_v}
    )

if(__name__) == '__main__':
        import uvicorn
        uvicorn.run(
        "main:app",
        host    = "0.0.0.0",
        port    = 8080,
        reload  = True
    )

