from fastapi import APIRouter, Depends, HTTPException
from models import ExerciseRoutineModel, UserModel, UpdateExerciseRoutineModel
from database import get_routines, update_routine, get_routine_id, get_routine_user, get_user_id
from auth import Depends, get_current_user


routines_route = APIRouter()

@routines_route.get("/api/routines/all")
async def get_all_routines():
    all_routines = await get_routines()
    return all_routines

async def get_base_routines():

    # Crear la rutina de principiante
    beginner_routine = ExerciseRoutineModel(
        modify_level= "base",
        name="Rutina Cuerpo Completo Principiante",
        level="Principiante",
        exercises=[
            {"name": "Flexiones", "exercise_type": "tren superior", "sets": 3, "rest_between_sets": 90},
            {"name": "Dominadas Australianas", "exercise_type": "tren superior", "sets": 3, "rest_between_sets": 90},
            {"name": "Sentadillas", "exercise_type": "tren inferior", "sets": 3, "rest_between_sets": 90},
            {"name": "Zancadas", "exercise_type": "tren inferior", "sets": 3, "rest_between_sets": 90},
            {"name": "Plancha", "exercise_type": "core", "sets": 3, "rest_between_sets": 90},  # 1 repetición puede significar tiempo
        ],
        rest_between_exercises=180
    )

    # Crear la rutina intermedia
    intermediate_routine = ExerciseRoutineModel(
        modify_level= "base",
        name="Rutina Cuerpo Completo Intermedio",
        level="Intermedio",
        exercises=[
            {"name": "Flexiones en pica", "exercise_type": "tren superior", "sets": 4, "rest_between_sets": 120},
            {"name": "Flexiones", "exercise_type": "tren superior", "sets": 3, "rest_between_sets": 120},
            {"name": "Dominadas supinas", "exercise_type": "tren superior", "sets": 4, "rest_between_sets": 120},
            {"name": "Dominadas Australianas", "exercise_type": "tren superior", "sets": 3, "rest_between_sets": 120},
            {"name": "Sentadillas", "exercise_type": "tren inferior", "sets": 4, "rest_between_sets": 120},
            {"name": "Zancadas", "exercise_type": "tren inferior", "sets": 3, "rest_between_sets": 120},
            {"name": "Elevacion de Tobillos", "exercise_type": "tren inferior", "sets": 4, "rest_between_sets": 120},
            {"name": "Hollow Body", "exercise_type": "core", "sets": 3, "rest_between_sets": 120},
        ],
        rest_between_exercises=180
    )

    # Crear la rutina avanzada
    advanced_routine = ExerciseRoutineModel(
        modify_level= "base",
        name="Rutina Cuerpo Completo Avanzado",
        level="Avanzado",
        exercises=[
            {"name": "Fondos en paralelas", "exercise_type": "tren superior", "sets": 4, "rest_between_sets": 120},
            {"name": "Flexiones en Pica", "exercise_type": "tren superior", "sets": 4, "rest_between_sets": 120},
            {"name": "Dominadas Pronas", "exercise_type": "tren superior", "sets": 4, "rest_between_sets": 120},
            {"name": "Dominadas Australianas", "exercise_type": "tren superior", "sets": 4, "rest_between_sets": 120},
            {"name": "Sentadillas con salto", "exercise_type": "tren inferior", "sets": 4, "rest_between_sets": 120},
            {"name": "Zancadas con salto", "exercise_type": "tren inferior", "sets": 4, "rest_between_sets": 120},
            {"name": "Peso muerto a una pierna", "exercise_type": "tren inferior", "sets": 4, "rest_between_sets": 120},
            {"name": "Elevacion de tobillos con peso", "exercise_type": "tren inferior", "sets": 4, "rest_between_sets": 120},
            {"name": "L-sit", "exercise_type": "core", "sets": 4, "rest_between_sets": 120},
        ],
        rest_between_exercises=300
    )

    # Crear la rutina de calentamiento

#    warmup_routine = ExerciseRoutineModel(
 #       name="Rutina de Calentamiento",
  #      level="calentamiento",
   #     exercises=[
    #        {"name": "Estiramientos dinámicos", "exercise_type": "flexibilidad", "sets": 1, "rest_between_sets": 0},
     #       {"name": "Rotación de hombros", "exercise_type": "tren superior", "sets": 1, "rest_between_sets": 0},
      #      {"name": "Rotación de cadera", "exercise_type": "tren inferior", "sets": 1, "rest_between_sets": 0},
       #     {"name": "Caminata en el sitio", "exercise_type": "cardio", "sets": 1, "rest_between_sets": 0},
        #    {"name": "Saltos suaves", "exercise_type": "cardio", "sets": 1, "rest_between_sets": 0},
        #],
        #rest_between_exercises=30  # Un descanso corto entre ejercicios de calentamiento
    #)

    return [beginner_routine, intermediate_routine, advanced_routine]


@routines_route.get("/api/routines/{id}", response_model=ExerciseRoutineModel)
async def get_one_routine(id: str):
    one_routine = await get_routine_id(id)
    if one_routine:
        return one_routine
    raise HTTPException(404, f"Routine with id {id} not found")
    

routines_route.put("/api/routines/{id}", response_model= ExerciseRoutineModel)
async def edit_routine(id: str, routine: UpdateExerciseRoutineModel):
    response = await update_routine(id, routine)
    if response:
        return response
    raise HTTPException(404, f"Routine with id {id} not found")

@routines_route.post("/assign-routine")
async def assign_routine(current_user: UserModel = Depends(get_current_user)):
    # Verificar el campo `disc_or_dise` del usuario
    modify_level = None

    if current_user.disc_or_dise == "Ninguna":
        modify_level = "base"
    elif current_user.disc_or_dise == "Enfermedad Cardiaca o Respiratoria":
        modify_level = "mod_lev1"
    elif current_user.disc_or_dise in ["Lesion leve en brazo/s"]:
        modify_level = "mod_lev2"
    elif current_user.disc_or_dise in ["Lesion leve en pierna/s"]:
        modify_level = "mod_lev3"

    # Obtener el nivel de entrenamiento del usuario
    level = current_user.training_level

    # Llamar a la función para buscar una rutina basada en `modify_level` y `level`
    routine = await get_routine_user(modify_level, level, current_user.id)

    if routine:
        # Retornar la rutina en formato JSON para el frontend
        return {"routine_name": routine["name"], "routine_id": str(routine["_id"])}
    else:
        raise HTTPException(status_code=404, detail="Routine could not be assigned")
    
@routines_route.get("/api/routines/intermediate/user/{id}")
async def get_user_ifullbody_routine(id: str):
    # Buscar el usuario por ID
    user = await get_user_id(id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener los IDs de las rutinas asociadas al usuario
    routine_ids = user.get("routine_ids", [])
    
    if not routine_ids:
        raise HTTPException(status_code=404, detail="No se encontraron rutinas para este usuario")
    
    # Iterar sobre los IDs de rutinas y buscar la rutina cuyo nombre contenga "Cuerpo Completo"
    for routine_id in routine_ids:
        routine = await get_routine_id(routine_id)
        if routine and "Cuerpo Completo" and "Intermedio" in routine.get("name", ""):
            # Retornar la rutina si se encuentra
            return {
                "name": routine["name"], 
                "exercises": routine["exercises"],
                "rest_between_exercises": routine["rest_between_exercises"]
                

            }
    
    # Si ninguna rutina coincide con "Cuerpo Completo"
    raise HTTPException(status_code=404, detail="No se encontró una rutina de 'Cuerpo Completo' para este usuario")

    
@routines_route.get("/api/routines/Advance/user/{id}")
async def get_user_afullbody_routine(id: str):
    # Buscar el usuario por ID
    user = await get_user_id(id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener los IDs de las rutinas asociadas al usuario
    routine_ids = user.get("routine_ids", [])
    
    if not routine_ids:
        raise HTTPException(status_code=404, detail="No se encontraron rutinas para este usuario")
    
    # Iterar sobre los IDs de rutinas y buscar la rutina cuyo nombre contenga "Cuerpo Completo"
    for routine_id in routine_ids:
        routine = await get_routine_id(routine_id)
        if routine and "Cuerpo Completo" and "Avanzado" in routine.get("name", ""):
            # Retornar la rutina si se encuentra
            return {
                "name": routine["name"], 
                "exercises": routine["exercises"],
                "rest_between_exercises": routine["rest_between_exercises"]
                

            }
    
    # Si ninguna rutina coincide con "Cuerpo Completo"
    raise HTTPException(status_code=404, detail="No se encontró una rutina de 'Cuerpo Completo' para este usuario")

@routines_route.get("/api/routines/Begginer/user/{id}")
async def get_user_bfullbody_routine(id: str):
    # Buscar el usuario por ID
    user = await get_user_id(id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener los IDs de las rutinas asociadas al usuario
    routine_ids = user.get("routine_ids", [])
    
    if not routine_ids:
        raise HTTPException(status_code=404, detail="No se encontraron rutinas para este usuario")
    
    # Iterar sobre los IDs de rutinas y buscar la rutina cuyo nombre contenga "Cuerpo Completo"
    for routine_id in routine_ids:
        routine = await get_routine_id(routine_id)
        if routine and "Cuerpo Completo" and "Principiante" in routine.get("name", ""):
            # Retornar la rutina si se encuentra
            return {
                "name": routine["name"], 
                "exercises": routine["exercises"],
                "rest_between_exercises": routine["rest_between_exercises"]
            }
    
    # Si ninguna rutina coincide con "Cuerpo Completo"
    raise HTTPException(status_code=404, detail="No se encontró una rutina de 'Cuerpo Completo' para este usuario")

@routines_route.get("/api/routines/user/{id}")
async def get_user_fullbody_routine(id: str):
    # Buscar el usuario por ID
    user = await get_user_id(id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener los IDs de las rutinas asociadas al usuario
    routine_ids = user.get("routine_ids", [])
    
    if not routine_ids:
        raise HTTPException(status_code=404, detail="No se encontraron rutinas para este usuario")
    
    # Iterar sobre los IDs de rutinas y buscar la rutina cuyo nombre contenga "Cuerpo Completo"
    for routine_id in routine_ids:
        routine = await get_routine_id(routine_id)
        if routine and "Cuerpo Completo" in routine.get("name", ""):
            # Retornar la rutina en el formato esperado
            return {"routine_name": routine["name"]}
    
    raise HTTPException(status_code=404, detail="Rutina de cuerpo completo no encontrada")