from backend.scraper import *

from fastapi import FastAPI, Request, Form

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import uvicorn


app = FastAPI()

# if __name__ == "__main__":
#     port = int(os.getenv("PORT", 8000))  # Default to 8000 if PORT is not set
#     uvicorn.run(app, host="0.0.0.0", port=port)

# # Setup Jinja2 templates & static files
# templates = Jinja2Templates(directory="backend/templates")
# app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# @app.get("/")
# async def serve_form(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

class FormData(BaseModel):
    business_name: str
    date: str
    test_type: str = ""
    test_staff: str = ""
    time: str = ""


@app.post("/get_appointments/")
async def get_appointments(data: FormData):

    function_mappings = {
        'Dexafit Detroit': 'dexafit',
        'E3 Fitology': 'e3fitology',
        'Dexa NYC': 'squareup'
    }

    json_response = globals()[f'get_{function_mappings[data.business_name]}'] \
                             (data.date, type=data.test_type, staff=data.test_staff)
    
    return {
        **json_response, 
        'business_name': data.business_name,
        'date': data.date,
        'test_type': data.test_type,
        'test_staff': data.test_staff,
    }
    
    # return templates.TemplateResponse("index.html", {
    #     "request": request, 
    #     "business_name": business_name,
    #     "date": date,
    #     "submitted": True,
    #     "appointments": response['slots'],
    #     "form_submitted": True,
    # })

@app.post('/confirm_appointment/')
async def confirm_appointment(data: FormData):
    function_mappings = {
        'Dexafit Detroit': 'dexafit',
        'E3 Fitology': 'e3fitology',
        'Dexa NYC': 'squareup'
    }

    json_response = globals()[f'get_{function_mappings[data.business_name]}'] \
                             (data.date, type=data.test_type, staff=data.test_staff)
    
    found = False

    for slot in json_response['slots']:
        if slot['formatted_time'] == data.time:
            found = True
            break

    return {'message': 'Appointment confirmed!' if found else 'Appointment not found.'}
