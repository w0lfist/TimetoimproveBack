from pydantic import BaseModel, Field, EmailStr
from typing import Any, Optional, Literal, Union
from bson import ObjectId
from schemas.routine_schema import ExerciseRoutineModel

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any, field: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        try:
            return ObjectId(str(v))
        except Exception:
            raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        schema = handler(schema)
        schema.update(type="string")
        return schema
    
class TagsModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    day: Literal["Lunes","Martes","Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    state: Optional[Literal["Sin iniciar", "Completada","Incompleta"]] = "Sin iniciar"
    routine: Optional[str] = None

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        from_attributes = True
        arbitrary_types_allowed = True

class UpdateTagsModel(BaseModel):
    day: Optional[str] = None
    state: Optional[Literal["Sin iniciar", "Completada", "Incompleta"]] = None
    routine: Optional[str] = None

class TagCreate(BaseModel):
    user_id: str
    days: list[Literal["Lunes","Martes","Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]]
    routine: str