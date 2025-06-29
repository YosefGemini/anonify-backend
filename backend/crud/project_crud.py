
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from models import project_model, author_model
from schemas.project import ProjectBase, ProjectUpdate, Project, ProjectCreate, ProjectDelete
from crud.dataset_crud import delete_dataset




def create_project(db: Session, project: ProjectCreate):
    project_in_db = db.query(project_model.Project).filter(project_model.Project.title == project.title).first()
    if project_in_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Project with name {project.title} already exists")

    db_project = project_model.Project(
        title=project.title,
        description=project.description,
        author_id=project.author_id
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project

def get_project(db: Session, project_id: str):

    print("Fase 1 de test ADD Entities")

    db_project = db.query(project_model.Project).filter(project_model.Project.id == project_id).first()
    return db_project

def get_all_projects(db: Session):

    return db.query(project_model.Project).all()

def get_all_projects_by_author(db: Session, author_id: str):
    return db.query(project_model.Project).filter(project_model.Project.author_id == author_id).all()

def update_project(db: Session, project: ProjectUpdate):

    db_project = db.query(project_model.Project).filter(project_model.Project.id == project.id).first()
    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Project with id {project.id} not found")

    db_project.title = project.title
    db_project.description = project.description

    db.commit()
    db.refresh(db_project)

    return db_project

def delete_project(db: Session, project_id: str):

    db_project = db.query(project_model.Project).filter(project_model.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Project with id {project_id} not found")
    
    projects_datasets = db_project.datasets


    if (len(projects_datasets)>0):
        for dataset in projects_datasets:
            dataset_id = str(dataset.id)
            delete_dataset(db=db, dataset_id=dataset_id)

    db.delete(db_project)
    db.commit()

    #TODO
    # Eliminar carpetas de proyectos eliminados

    return db_project






    db.delete(db_project)
    db.commit()
    return 

def share_project(db: Session, project_id: str, users: list[str]):

    project_in_db = db.query(project_model.Project).filter(project_model.Project.id == project_id).first()

    if not project_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project with id {project_id} not found")
    
    users_to_share = []
    
    for user_id in users:
        user_in_db = db.query(author_model.Author).filter(author_model.Author.id == user_id)
        if not user_in_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user with id: {user_id}not found in DB")
        
        users_to_share.append(user_in_db)


    print(f"Usuarios a compartir: ", users_to_share)
    db_project = project_model.Project(
        shared = users_to_share
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

