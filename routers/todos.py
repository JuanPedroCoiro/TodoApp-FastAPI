from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from models import Todos
from routers.auth import get_current_user, db_dependency
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

templates = Jinja2Templates(directory="templates")


# --- Pages ---
@router.get("/todo-page")
def todo_page(request: Request, db: db_dependency, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # Filtrar solo los todos del usuario logueado
    todos = db.query(Todos).filter(Todos.owner_id == current_user["user_id"]).all()

    # Convertir a lista de diccionarios para Jinja2
    todos_list = [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "complete": t.complete
        } for t in todos
    ]

    return templates.TemplateResponse("todos.html", {"request": request, "todos": todos_list, "user": current_user})


# --- Page para editar un todo ---
@router.get("/edit-todo-page/{todo_id}")
def edit_todo_page(todo_id: int, request: Request, db: db_dependency, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # Buscar el todo y asegurarse de que sea del usuario logueado
    todo = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == current_user["user_id"]).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    todo_data = {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "priority": todo.priority,
        "complete": todo.complete
    }

    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo_data, "user": current_user})


# --- Endpoints ---
@router.get("/todo", response_model=None)
async def get_all_todos(db: db_dependency, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    todos = db.query(Todos).all()
    return [dict(
        id=t.id,
        title=t.title,
        description=t.description,
        priority=t.priority,
        complete=t.complete
    ) for t in todos]


@router.get("/add-todo-page")
def add_todo_page(request: Request, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return templates.TemplateResponse("add-todo.html", {"request": request})


@router.post("/todo", response_model=None)
async def create_todo(request: Request, db: db_dependency, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    data = await request.json()

    new_todo = Todos(
        title=data["title"],
        description=data.get("description", ""),
        priority=data.get("priority", 1),
        complete=data.get("complete", False),
        owner_id=current_user["user_id"]  # <-- asignar el id del usuario logueado
    )

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return {"message": "Todo created", "id": new_todo.id}


@router.put("/todo/{todo_id}", response_model=None)
async def update_todo(todo_id: int, request: Request, db: db_dependency,
                      current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    data = await request.json()
    todo.title = data.get("title", todo.title)
    todo.description = data.get("description", todo.description)
    todo.priority = data.get("priority", todo.priority)
    todo.complete = data.get("complete", todo.complete)
    db.commit()
    return {"message": "Todo updated"}


@router.delete("/todo/{todo_id}", response_model=None)
async def delete_todo(todo_id: int, db: db_dependency, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted"}
