from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates

from src.logger import CustomLogger
LOGGER = CustomLogger(__name__).logger

templates = Jinja2Templates(directory="src/templates")

router_main = APIRouter(
    prefix="",
    tags=["Pages"]
)

@router_main.get("/")
async def read_index(request: Request): 
    try:
        LOGGER.info("Main page requested")
        return templates.TemplateResponse("main_page.html", {"request": request})
    except Exception as exc:
        LOGGER.error("Main page request failed %d",exc, exc_info=True)
        raise HTTPException(status_code=500, detail={
            "status": "Server error",
            "data": exc,
            "details": "Template loading error"
        })

router_login = APIRouter(
    prefix="",
    tags=["Pages"]
)

@router_login.get("/login")
async def read_index(request: Request): 
    try:
        LOGGER.info("Login page requested")
        return templates.TemplateResponse("userpage.html", {"request": request})
    except Exception as exc:
        LOGGER.error("Main page request failed %d",exc, exc_info=True)
        raise HTTPException(status_code=500, detail={
            "status": "Server error",
            "data": exc,
            "details": "Template loading error"
        })
