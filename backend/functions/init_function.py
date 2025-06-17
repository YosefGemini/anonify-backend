from sqlalchemy.orm import Session
from models.role_model import Role
# from models.user_model import User

# from models.author_model import 

from schemas.permission import PermissionCreate
from models.permission_model import Permission
from crud.author_crud import create_author
from schemas.author import AuthorCreate
# usuarios, roles , permisos por defecto 

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
    }
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


DEFAULT_ROLES = {
    "administrator": [
        # permisos de usuarios
    "create_user",
    "view_user",
    "edit_user",
    "delete_user",
    
    # permisos de roles
    "create_role",
    "view_role",
    "edit_role",
    "delete_role",

    # permisos de proyectos


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
    

    ],
    "preprocesing-operator": [

        "view_data",
        "edit_data",
        "view_project",
        # "edit_project"
        "view_dataset",
        "preprocess_dataset",
        ],
    "anonimazing-operator": [

        "view_data",
        "edit_data",
        "view_project",
        # "edit_project"
        "view_dataset",
        "anonymize_dataset",
    ],

    # "data-scientist": ["view_data", "analyze_data", "train_model"],
    # "data-engineer": ["view_data", "analyze_data", "train_model", "deploy_model"],
    # "data-visualization": ["view_data", "analyze_data", "create_visualization"],
    # "data-architect": ["view_data", "analyze_data", "train_model", "deploy_model", "create_visualization"],

    "data-governance": [
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
    ],
    "viewer": ["view_data"],

}

async def init_roles_and_permissions(db):


    print("----------------------------------------------------------\n")
    print("Iniciando la base de datos con los roles y permisos por defecto")
    print("----------------------------------------------------------\n")


    
    # Crear permisos por defecto
    print("Creando permisos por defecto")
    print("----------------------------------------------------------\n")

    for permission in DEFAULT_PERMISSIONS:
        perm = db.query(Permission).filter(Permission.name == permission.name).first()

        print("permiso", perm)
        if not perm:
            perm = Permission(
                name=permission.name,
                description=permission.description
            )
            db.add(perm)
            db.commit()
            db.refresh(perm)
    # Crear roles por defecto
    print("Creando roles por defecto")
    print("----------------------------------------------------------\n")

    for role_name, perms in DEFAULT_ROLES.items():



        role = db.query(Role).filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            db.add(role)
            db.commit()
            db.refresh(role)
        
        for perm_name in perms:
            perm = db.query(Permission).filter_by(name=perm_name).first()
            if not perm:
                perm = Permission(name=perm_name)
                db.add(perm)
                db.commit()
                db.refresh(perm)
            
            if perm not in role.permissions:
                role.permissions.append(perm)
        
        db.commit()
    
    print("----------------------------------------------------------\n")
    print("Creando usuarios por defecto")
    print("----------------------------------------------------------\n")

    default_admin: AuthorCreate = {
        "name": "DefaultAdmin",
        "nationality": "No Especificado",
        "username": "admin",
        "password": "admin",
        "mail": "admin@mail.com",
        "cell_phone": "123456789",
        "role_id": db.query(Role).filter_by(name="administrator").first().id,

    } 
    # Crear usuario por defecto
    createuser = await create_author(db, default_admin)
    if not createuser:
        print("Error al crear el usuario por defecto")
        return
    
    print("----------------------------------------------------------\n")
    print(createuser)

    print("----------------------------------------------------------\n")
    print("Usuario por defecto creado")
    print("----------------------------------------------------------\n")
    



    print("----------------------------------------------------------")
    print("Base de datos inicializada con los roles y permisos por defecto")
    print("----------------------------------------------------------")

