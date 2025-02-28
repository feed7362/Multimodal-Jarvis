from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="src/templates")

router_main = APIRouter(
    prefix="",
    tags=["Pages"]
)

@router_main.get("/")
async def read_index(request: Request): 
    try:
        return templates.TemplateResponse("main_page.html", {"request": request})
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "Server error",
            "data": None,
            "details": "Template loading error"
        })

router_login = APIRouter(
    prefix="",
    tags=["Pages"]
)

@router_login.get("/login")
async def read_index(request: Request): 
    try:
        return templates.TemplateResponse("userpage.html", {"request": request})
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "Server error",
            "data": None,
            "details": "Template loading error"
        })
