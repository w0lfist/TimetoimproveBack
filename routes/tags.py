from fastapi import APIRouter, Depends, HTTPException, status
from database import get_tags, create_tag, get_one_tag, get_tag_user, get_routine_id_o, get_user_id, get_tags_user, get_tag_user_id, update_tag, update_tags, tags_collection, delete_tag
from models import TagsModel, UpdateTagsModel, UserModel, TagCreate, ObjectId
from datetime import timedelta
import asyncio
from typing import List
from auth import oauth2_scheme, get_current_user


tag_route = APIRouter()


@tag_route.get("/tag/all-tags")
async def get_all_tags():
    all_tags = await get_tags()
    return all_tags

@tag_route.get("/tag/{id}")
async def get_tag(id: str):
    one_tag = await get_one_tag(id)
    if one_tag:
        return one_tag
    raise HTTPException(404, f"Tag with id {id} not found")

@tag_route.post("/tag/create")
async def create_tag_endpoint(tag_data: TagsModel):
    user_id = tag_data.user_id
    day = tag_data.day  # Día seleccionado por el usuario

    # Comprobar si ya existe una tarjeta para el usuario en el día seleccionado
    existing_tag = await get_tag_user(user_id, day)
    if existing_tag:
        raise HTTPException(status_code=400, detail="Este día ya está ocupado.")

    # Obtener el usuario para acceder a sus rutinas
    user = await get_user_id(user_id)
    # Buscar la rutina del usuario
    routine_names = []
    routine_ids = user.get("routine_ids", [])
    
    for routine_id in routine_ids:
        routine = await get_routine_id_o(routine_id)
        if routine:
            routine_names.append(routine.name)

    # Elegir la rutina
    tag_data.routine = routine_names[0] if routine_names else "Rutina no asignada"

    # Crear la tarjeta
    created_tag = await create_tag(tag_data)
    created_tag["_id"] = str(created_tag["_id"])  # Asegúrate de que el ID sea un string

    tag_id = str(created_tag["id"])  # Convierte ObjectId a cadena si es necesario

    return {
        "id": tag_id,
        "day": created_tag["day"],
        "message": "Tarjeta creada correctamente"  # Mensaje de éxito
    }

@tag_route.get("/api/tags/user/{id}")
async def get_tags_from_user(id):
    user_id = id
    user = await get_user_id(user_id)
    if user:
        tag_user_id = id
    else:
        raise HTTPException(status_code=404, detail="El usuario con el id:{id} no existe")

    tags_user = await get_tags_user(tag_user_id)
    if tags_user:
        return tags_user
    else:
        raise HTTPException(status_code=404, detail="El usuario con el id:{id} no ha creado ninguna rutina")



@tag_route.put("/api/tag/user/{id}", response_model=UpdateTagsModel)
async def edit_tag(id: str, tag: UpdateTagsModel):
    tag_user = await tags_collection.find_one({"_id": ObjectId(id)})

    if tag_user:  # Asegúrate de que existe el tag para actualizar
        response = await update_tag(id, tag)
        return response

    raise HTTPException(status_code=404, detail=f"Tag with id {id} not found")


@tag_route.put("/api/tags/reset/user/{user_id}", response_model=list[UpdateTagsModel])
async def reset_tags(user_id: str):
    # Busca las tarjetas del usuario
    tags = await get_tag_user_id(user_id)

    if not tags:
        raise HTTPException(status_code=404, detail="No tags found for this user.")

    updated_tags = []
    for tag in tags:
        tag_data = {"day": tag["day"], "state": "Sin iniciar", "routine": tag["routine"]}
        # Actualiza el estado de cada tag
        await update_tags(tag["_id"], tag_data)
        updated_tags.append(tag_data)

    return updated_tags

@tag_route.delete("/api/tags/eliminate/user/{user_id}", response_model=list[UpdateTagsModel])
async def eliminate_tags(user_id: str):
    # Busca las tarjetas del usuario
    tags = await get_tag_user_id(user_id)

    if not tags:
        raise HTTPException(status_code=404, detail="No tags found for this user.")

    delete_tags = []
    for tag in tags:
        tag_id = tag["_id"]
        try:
            # Elimina cada tag usando la función delete_tag
            await delete_tag(tag_id)
            delete_tags.append(tag)  # Agrega el tag eliminado a la lista de eliminados
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete tag with id {tag_id}: {str(e)}")

    return delete_tags
        
@tag_route.delete("/api/delete/tag/user/{tag_id}")
async def delete_task(tag_id: str):
    try:
        result = await delete_tag(tag_id)

        # Verifica si se eliminó algún documento
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Task not found")

        return {"detail": "Task deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))