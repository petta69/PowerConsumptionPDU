import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")

# Path to your image on disk
IMAGE_PATH = os.path.abspath("static/powerchart.png")

def cache_bust(static_path) -> str:
    # FIX: Convert the Starlette URL object to a plain string first
    static_path_str = str(static_path)
    
    base_dir = os.path.abspath(".") 
    local_path = os.path.join(base_dir, static_path_str.lstrip("/"))
    
    if os.path.exists(local_path):
        mtime = int(os.path.getmtime(local_path))
        return f"{static_path_str}?v={mtime}"
    
    print(f"DEBUG: File not found at {local_path}") 
    return static_path_str

templates.env.filters["cache_bust"] = cache_bust

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")

# NEW: Endpoint for JavaScript to poll
@app.get("/api/image-version")
async def get_image_version():
    if os.path.exists(IMAGE_PATH):
        mtime = int(os.path.getmtime(IMAGE_PATH))
        return JSONResponse({"version": mtime})
    return JSONResponse({"version": 0})



if(__name__) == '__main__':
        import uvicorn
        uvicorn.run(
        "main:app",
        host    = "0.0.0.0",
        port    = 8080,
        reload  = True
    )

