from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal,Optional
import json
import os

app = FastAPI()

FILE_NAME = "patients.json"


# Patient Model

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="Id of the patient", examples=["P001"])]
    name: Annotated[str, Field(..., description="Name of the patient")]
    city: Annotated[str, Field(..., description="City where the patient is living")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the patient")]
    gender: Annotated[
        Literal["Male", "Female", "Others"],
        Field(..., description="Gender of the patient"),
    ]
    height: Annotated[
        float, Field(..., gt=0, description="Height of the patient in meters")
    ]
    weight: Annotated[
        float, Field(..., gt=0, description="Weight of the patient in KG")
    ]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"


# Update

class patientipdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None)]
    gender: Annotated[
        Optional[Literal["Male", "Female", "Others"]],
        Field(default=None),
    ]
    height: Annotated[Optional
        [float], Field(default=None)
    ]
    weight: Annotated[Optional
        [float], Field(default=None)
    ]

# Utility Functions
def load_data():
    if not os.path.exists(FILE_NAME):
        return {}
    with open(FILE_NAME, "r") as f:
        return json.load(f)


def save_data(data):
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)


# Routes
@app.get("/")
def home():
    return {"message": "Patients Management System API"}


@app.get("/about")
def about():
    return {"message": "A Fully Functional API to manage patient records"}


@app.get("/view")
def view_all():
    return load_data()


# Get Single Patient

@app.get("/patient/{patient_id}")
def view_patient(
    patient_id: str = Path(..., description="ID of the patient", examples=["P001"])
):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {patient_id: data[patient_id]}


# Create Patient

@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient already exists")

    data[patient.id] = patient.model_dump(exclude=["id"])
    save_data(data)

    return JSONResponse(
        status_code=201,
        content={"message": "Patient created successfully"},
    )


# Sort Patients

@app.get("/sort")
def sort_patients(
    sort_by: str = Query(..., description="Sort by age, height, weight, or bmi"),
    order: str = Query("asc", description="asc or desc"),
):
    valid_fields = ["age", "height", "weight", "bmi"]

    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid field. Choose from {valid_fields}",
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="Order must be asc or desc",
        )

    data = load_data()

    reverse_order = True if order == "desc" else False

    sorted_data = sorted(
        data.items(),
        key=lambda x: x[1].get(sort_by, 0),
        reverse=reverse_order,
    )

    return dict(sorted_data)

@app.put("/edit/{patient_id}")
def update_patient(patient_id:str,patient_upadte : patientipdate):
    
    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code=404,detail='Patient Not found!')
    
    existing_patient_info =data[patient_id]
    
    update_patient_info =   patient_upadte.model_dump(exclude_unset=True)
    
    for key ,value in update_patient_info.items():
        existing_patient_info[key]= value
        
        
    existing_patient_info['id'] = patient_id    
    patient_pydantic_obj = Patient(**existing_patient_info) 
    existing_patient_info = patient_pydantic_obj.model_dump(exclude='id')  
     
    # add this dict to data
    
    data[patient_id]= existing_patient_info
    # save data
    save_data(data)
    
    return JSONResponse(status_code=200,content={'massage':'patient updated'})
    

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id :str):
    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code=404,detail='patient Not found') 
    
    
    del data[patient_id]
    
    save_data(data)
    
    return JSONResponse(status_code=200,content={'massage':'patient deleted '})