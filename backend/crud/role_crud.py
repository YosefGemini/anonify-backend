

from models import role_model, permission_model
from schemas.role import RoleCreate, RoleUpdate, Role
from sqlalchemy.orm import Session, joinedload

from fastapi import HTTPException, status
from functions import auth_token

from uuid import UUID

DEFAULT_ROLES: list[RoleCreate] = [
    {
        "name": "admin",
        "description": "Administrator role with all permissions",
        "permissions": [
            "create_user",
            "view_user",
            "edit_user",
            "delete_user",
            "create_role",
            "view_role",
            "edit_role",
            "delete_role",
            "create_project",
            "view_project",
            "edit_project",
            "delete_project",
            "create_entity",
            "view_entity",
            "edit_entity",
            "delete_entity",
            "view_permission",
            "edit_permission"
                    
        ]
    },
    {
        "name": "preprocesing-operator",
        "description": "Preprocessing operator role with limited permissions",
        "permissions": [
            "view_data",
            "edit_data",
            "view_project",
        # "edit_project"
            "view_dataset",
            "preprocess_dataset",
            "view_entity",
            
            
        ]
    },
    {
        "name": "anonymization-operator",
        "description": "Anonymization operator role with limited permissions",
        "permissions": [
            "view_data",
            "edit_data",
            "view_project",
        # "edit_project"
            "view_dataset",
            "anonymize_dataset",
            "view_entity",
            "create_entity",
        ]
    },
    {
        "name": "data-governance",
        "description": "Data governance role with limited permissions",
        "permissions": [
            "create_project",
            "view_project",
            "edit_project",
            "delete_project",
            # permisos de datasets
            "create_dataset",
            "view_dataset",
            "edit_dataset",
            "delete_dataset",
            "preprocess_dataset",
            "anonymize_dataset",
    
            #permisos de datos

            "view_data",
            "edit_data",
            "download_data",
            "upload_data",
            "view_entity",
            "create_entity",
            "edit_entity",
            "delete_entity"
        ]
    },
    {
        "name": "viewer",
        "description": "Viewer role with limited permissions",
        "permissions": [
            "view_project",
            "view_dataset",
            "view_data",
            "view_entity",
        ],

    }
    

]



async def create_default_roles(db):
    try:
        for role in DEFAULT_ROLES:
            # print(f"Role: {role['name']}")
            
            role_in_db = db.query(role_model.Role).filter(role_model.Role.name == role["name"]).first()

            if not role_in_db:
                permission_to_add = []
                for permission in role["permissions"]:

                    # print (f"Permission: {permission}")

                    permission_in_db = db.query(permission_model.Permission).filter(permission_model.Permission.name == permission).first()
                    # print("Fase 1")
                # permission_in_db = db.query(role_model.permission).filter(role_model.Permission.name == permission).first()
                    if not permission_in_db:

                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Permission not found")

                    # print("Fase 2")
                    permission_to_add.append(permission_in_db)
                    # print("Fase 3", permission_to_add)

                # print("role name", role["name"])
                # print("role description", role["description"])
                # print("role permissions", permission_to_add)
                db_role = role_model.Role(
                    name=role["name"],
                    description=role["description"],
                    permissions=permission_to_add
                )
                # print("Fase 4")

                db.add(db_role)
                db.commit()
                db.refresh(db_role)
                print(f"Role {role['name']} created")

            else:
                # raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                print(f"Role with name {role_in_db.name} already exists") 
                            # detail=f"Role with name {role['name']} already exists")



           
                            # detail=f"Role with name {role_in_db.name} already exists"
        
    except Exception as e:
        print(f"Error creating default roles: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error creating default roles")


def create_role(db, role: RoleCreate):
    role_in_db = db.query(role_model.Role).filter(role_model.Role.name == role.name).first()

    if role_in_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Role with name {role.name} already exists")

    db_role = role_model.Role(
        name=role.name,
        description=role.description
    )

    db.add(db_role)
    db.commit()
    db.refresh(db_role)

    return db_role
def get_role(db, role_id: UUID):
    role = db.query(role_model.Role).filter(role_model.Role.id == role_id).options(joinedload(role_model.Role.permissions)).first()

    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Role with id {role_id} not found")

    return role
def get_roles(db):
    roles = db.query(role_model.Role).all()

    if not roles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No roles found")

    return roles
def update_role(db, role_id: UUID, role: RoleUpdate):
    db_role = db.query(role_model.Role).filter(role_model.Role.id == role_id).first()

    if not db_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Role with id {role_id} not found")

    db_role.name = role.name
    db_role.description = role.description

    db.commit()
    db.refresh(db_role)

    return db_role
def delete_role(db, role_id: UUID):
    db_role = db.query(role_model.Role).filter(role_model.Role.id == role_id).first()

    if not db_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Role with id {role_id} not found")

    db.delete(db_role)
    db.commit()

    return {"detail": f"Role with id {role_id} deleted"}
