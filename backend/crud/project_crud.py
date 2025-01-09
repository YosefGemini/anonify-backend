
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from models import project_model

from schemas.project import ProjectBase, ProjectUpdate, Project, ProjectCreate, ProjectDelete




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

    db.delete(db_project)
    db.commit()
    return db_project