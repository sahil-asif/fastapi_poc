from backend.scraper import *

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


app = FastAPI()

# Setup Jinja2 templates & static files
templates = Jinja2Templates(directory="backend/templates")
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/")
async def serve_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit-form/")
async def process_form(
    request: Request,
    business_name: str = Form(...),
    date: str = Form(...),
    test_type: str = Form(''),
    test_staff: str = Form('')
):

    function_mappings = {
        'Dexafit Detroit': 'dexafit',
        'E3 Fitology': 'e3fitology',
        'Dexa NYC': 'squareup'
    }

    response = globals()[f'get_{function_mappings[business_name]}'](date, type=test_type, staff=test_staff)
    print(response)
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "business_name": business_name,
        "date": date,
        "submitted": True,
        "appointments": response['slots'],
    })
