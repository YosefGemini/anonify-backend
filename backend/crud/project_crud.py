
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

# def share_project(db: Session, project_id: str, users: list[str]):

#     project_in_db = db.query(project_model.Project).filter(project_model.Project.id == project_id).first()

#     if not project_in_db:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project with id {project_id} not found")
    
#     users_to_share = []
    
#     for user_id in users:
#         user_in_db = db.query(author_model.Author).filter(author_model.Author.id == user_id)
#         if not user_in_db:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user with id: {user_id}not found in DB")
        
#         users_to_share.append(user_in_db)


#     print(f"Usuarios a compartir: ", users_to_share)
#     db_project = project_model.Project(
#         shared = users_to_share
#     )

#     db.add(db_project)
#     db.commit()
#     db.refresh(db_project)

def share_project(db: Session, projectID: str, authors_id: list[str]):
  
    try:

        # 1. Fetch the project
        project_to_share = db.query(project_model.Project).filter(project_model.Project.id == projectID).first()
        if not project_to_share:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project with ID {projectID} not found")
        # Validacion de existencia del usuario en la base de datos
        authors_to_share = []
        for author_id in authors_id:
            author_in_db = db.query(author_model.Author).filter(author_model.Author.id == author_id).first()

            if not author_in_db:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {author_id} not found")
            

            authors_to_share.append(author_in_db)
        # validacion de que no tiene agregado el projecto previamente sinop agregar

        # 3. Add the project to each author's shared_projects relationship
        for author in authors_to_share:
            # total_projects = author.projects + author.shaded
            # exists = False
            # verificar si el proyecto ya es parte del usuario
            if project_to_share in author.projects: # Assuming 'projects' is the relationship for owned projects
                print(f"User {author.name} (ID: {author.id}) is already the owner of project {project_to_share.title}. Skipping sharing.")
                continue

            # Check if the project is already shared with this user
            if project_to_share in author.shared:
                print(f"Project {project_to_share.title} (ID: {projectID}) is already shared with user {author.name} (ID: {author.id}). Skipping.")
                continue

            # If not owned and not already shared, add it to the shared_projects collection
            author.shared.append(project_to_share)
            print(f"Project {project_to_share.title} shared with {author.name}.")

        # 4. Commit the changes to the database
        db.commit()
        db.refresh(project_to_share)
        print(f"Project {project_to_share.title} (ID: {projectID}) successfully shared with {len(authors_to_share)} users.")
            
        return project_to_share
                    

            # agregando proyectos propios
            # author.projects



    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"SERVER ERROR:{e}")