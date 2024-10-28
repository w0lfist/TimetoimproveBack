from pydantic import BaseModel, Field
from typing import Any, Optional, Literal
from bson import ObjectId

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

# Modelo para ejercicios individuales
class ExerciseModel(BaseModel):
    name: str  # Nombre del ejercicio
    exercise_type: Literal["tren superior", "core", "tren inferior"]
    sets: int  # Cantidad de series
    rest_between_sets: int  # Descanso entre series en segundos
    repetitions: Optional[str] = None  # Repeticiones por serie
    duration: Optional[str] = None # duracion del ejercicio

# Modelo de Rutinas
class ExerciseRoutineModel(BaseModel):
    id: ObjectId = Field(default_factory=PyObjectId, alias="_id")
    modify_level: Literal["base", "mod_lev1", "mod_lev2", "mod_lev3"]
    name: str  # Nombre de la rutina (ej: "Rutina Principiante", "Rutina Avanzado")
    level: Literal["Principiante", "Intermedio", "Avanzado"]  # Nivel de la rutina: "principiante", "intermedio", "avanzado"
    exercises: list[ExerciseModel]  # Lista de ejercicios
    rest_between_exercises: int  # Descanso entre ejercicios en segundos
    user_ids: list[PyObjectId] = []  # Lista de IDs de usuarios que usan esta rutina

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        from_attributes = True
        arbitrary_types_allowed = True

class UpdateExerciseRoutineModel(BaseModel):
    modify_level: Optional[Literal["mod_lev1", "mod_lev2", "mod_lev3"]] = None
    name: Optional[str] = None  # Nombre de la rutina (ej: "Rutina Principiante", "Rutina Avanzado")
    level: Optional[Literal["Principiante", "Intermedio", "Avanzado"]] = None  # Nivel de la rutina: "principiante", "intermedio", "avanzado"
    exercises: Optional[list[ExerciseModel]] = None  # Lista de ejercicios
    rest_between_exercises: Optional[int] = None # Descanso entre ejercicios en segundos
    user_ids: Optional[list[PyObjectId]] = None  # Lista de IDs de usuarios que usan esta rutina
    
    