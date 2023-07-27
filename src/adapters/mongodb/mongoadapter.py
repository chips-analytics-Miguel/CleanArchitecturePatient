from datetime import date
import datetime
from typing import List
from bson import ObjectId
from fastapi import HTTPException
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from src.domain.aggregats import Patient
from src.domain.schemas import PatientCreateSchema, PatientSchema
from src.interfaces.abstractrepository import PatientInterface
from src.config import settings

class MongoDBAdapter(PatientInterface):
    def __init__(self, mongo_uri: str):
        self.client = MongoClient(mongo_uri)
        self.db = self.client.get_database()

    def get_patient_collection(self) -> Collection:
        """Get patient collection"""
        return self.db.get_collection(settings.MONGO_COLLECTION)

    def save_patient(self, patient: dict) -> str:
        """Save patient."""
        #patient_dict = dict(patient)
        result = self.get_patient_collection().insert_one(patient)
        return str(result.inserted_id)
    
    def get_patient_by_id(self, patient_id: str) -> PatientSchema:
        """Get patient by id."""
        patient : PatientSchema = self.get_patient_collection().find_one({"_id": ObjectId(patient_id)}, {"_id": 0})
        if not patient:
            raise HTTPException(status_code=400,detail="Patient not found")
        return patient
    
    def get_patients(self) -> List[PatientSchema]:
        """Get patients."""
        patients = []
        for patient in self.get_patient_collection().find({}, {"_id": 0}) :
            patients.append(patient)
        return patients
    
    def update_patient(self, id:str,patient:PatientSchema):
        """Updates the patient."""
        data = dict(patient)
        self.get_patient_collection().find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": data},
        )   # noqa: WPS122
        return self.get_patient_collection().find_one({"_id": ObjectId(id)}, {"_id": 0})
    
    """def update_number(self,id:str, newphone: str)->PatientSchema:
        Updates the patient's phone number.
        patient = self.get_patient_by_id(id)
        patient["phone_number"] = newphone
        result = self.update_patient(id,patient)
        return result"""

    def del_patient(self, patient_id: str) -> str:
        """ Delete the patient."""
        patient = self.get_patient_collection().find_one({"_id": ObjectId(patient_id)})
        if patient:
            self.get_patient_collection().delete_one({"_id": ObjectId(patient_id)})
            return "Patient Deleted"
        return "NOT FOUND"

    def close(self):
        self.client.close()