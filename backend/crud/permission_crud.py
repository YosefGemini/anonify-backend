
from models.permission_model import Permission
from schemas.permission import PermissionCreate
from fastapi import HTTPException, status
from uuid import UUID
# from sqlalchemy.orm import Session

DEFAULT_PERMISSIONS: list[PermissionCreate] = [

    {
        "name": "create_user",
        "description": "Permite crear usuarios"
    }
    ,
    {
        "name": "view_user",
        "description": "Permite ver usuarios"
    }
    ,
    {
        "name": "edit_user",
        "description": "Permite editar usuarios"
    }
    ,
    {
        "name": "delete_user",
        "description": "Permite eliminar usuarios"
    }
    ,
    {
        "name": "create_role",
        "description": "Permite crear roles"
    }
    ,
    {
        "name": "view_role",
        "description": "Permite ver roles"
    }
    ,
    {
        "name": "edit_role",
        "description": "Permite editar roles"
    }
    ,
    {
        "name": "delete_role",
        "description": "Permite eliminar roles"
    },

    # ENTIDADES

    {
        "name": "create_entity",
        "description": "Permite crear roles"
    }
    ,
    {
        "name": "view_entity",
        "description": "Permite ver roles"
    }
    ,
    {
        "name": "edit_entity",
        "description": "Permite editar roles"
    }
    ,
    {
        "name": "delete_entity",
        "description": "Permite eliminar roles"
    }
    # {
    #     "name": "create_role",
    #     "description": "Permite crear roles"
    # }
    ,
    {
        "name": "view_permission",
        "description": "Permite ver los Permisos de cada usuario"
    }
    ,
    {
        "name": "edit_permission",
        "description": "Permite editar la descripción de los permisos"
    }
    # ,
    # {
    #     "name": "delete_role",
    #     "description": "Permite eliminar roles"
    # }
    ,
    {
        "name": "create_project",
        "description": "Permite crear proyectos"
    }
    ,
    {
        "name": "view_project",
        "description": "Permite ver proyectos"
    }
    ,
    {
        "name": "edit_project",
        "description": "Permite editar proyectos"
    }
    ,
    {
        "name": "delete_project",
        "description": "Permite eliminar proyectos"
    }
    ,
    {
        "name": "create_dataset",
        "description": "Permite crear datasets"
    }
    ,
    {
        "name": "view_dataset",
        "description": "Permite ver datasets"
    }
    ,
    {
        "name": "edit_dataset",
        "description": "Permite editar datasets"
    }
    ,
    {
        "name": "delete_dataset",
        "description": "Permite eliminar datasets"
    }
    ,
    {
        "name": "preprocess_dataset",
        "description": "Permite preprocesar datasets"
    }
    ,
    {
        "name": "anonymize_dataset",
        "description": "Permite anonimizar datasets"
    }
    ,
    {
        "name": "view_data",
        "description": "Permite ver datos"
    }
    ,
    {
        "name": "edit_data",
        "description": "Permite editar datos"
    }
    ,
    {
        "name": "download_data",
        "description": "Permite descargar datos"
    }
    ,
    {
        "name": "upload_data",
        "description": "Permite subir datos"
    }
    
]



async def create_default_permissions(db):

    try:

        for permission in DEFAULT_PERMISSIONS:
            permission_in_db = db.query(Permission).filter(Permission.name == permission['name']).first()

            if not permission_in_db:
                db_permission = Permission(
                    name=permission["name"],
                    description=permission["description"]
                )

                db.add(db_permission)
                db.commit()
                db.refresh(db_permission)
                print(f"Permission {permission['name']} created")
            else:
                print(f"Permission {permission['name']} already exists")
    except Exception as e:
        print(f"Error creating default permissions: {e}")
        raise


def create_permission(db, permission: PermissionCreate):
    permission_in_db = db.query(Permission).filter(Permission.name == permission.name).first()

    if permission_in_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Permission with name {permission.name} already exists")

    db_permission = Permission(
        name=permission.name,
        description=permission.description
    )

    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)

    return db_permission
def get_permission(db, permission_id: UUID):
    permission = db.query(Permission).filter(Permission.id == permission_id).first()

    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Permission with id {permission_id} not found")

    return permission
def get_permissions(db):
    permissions = db.query(Permission).all()

    if not permissions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No permissions found")

    return permissions
def update_permission(db, permission_id: UUID, permission: PermissionCreate):
    db_permission = db.query(Permission).filter(Permission.id == permission_id).first()

    if not db_permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Permission with id {permission_id} not found")

    db_permission.name = permission.name
    db_permission.description = permission.description

    db.commit()
    db.refresh(db_permission)

    return db_permission
def delete_permission(db, permission_id: UUID):
    db_permission = db.query(Permission).filter(Permission.id == permission_id).first()

    if not db_permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Permission with id {permission_id} not found")

    db.delete(db_permission)
    db.commit()

    return db_permission
def get_permissions_by_role(db, role_id: UUID):
    permissions = db.query(Permission).filter(Permission.roles.any(id=role_id)).all()

    if not permissions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No permissions found for role with id {role_id}")

    return permissions
def get_permissions_by_author(db, author_id: UUID):
    permissions = db.query(Permission).filter(Permission.roles.any(users.any(id=author_id))).all()

    if not permissions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No permissions found for author with id {author_id}")

    return permissions
