from pydantic import BaseModel,field_validator
from typing import List,Dict

class patient(BaseModel):
    name : str
    age  : int
    married:float
    allergies : List[str]
    contact_details : Dict[str,str]
    
    
    @field_validator('age',mode='after')
    @classmethod
    def validate_age(cls,value):
        if 0 < value < 100:
            return
        else:
            raise ValueError ("Age Between 0  to 100")

def insert_patient_data(patient:patient):
    print(patient.name)
    print(patient.age)  
    print("inserted")
    
patient_info = {'name':'nitish','age':30,'weight':65.2,'married':True,'allergies':['pollen','dust'],'contact_details':{'eamil':'abc@gmail.com','phone':'7201956334'}}

patient1 = patient(**patient_info)

insert_patient_data(patient1)

