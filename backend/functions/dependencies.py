from typing import List, Union
from fastapi import HTTPException, status, Depends

from functions.auth_token import validate_token_header

from schemas.author import AuthorToken

class HasPermission:
    def __init__(self, required_permissions: Union[str, List[str]]):
        if isinstance(required_permissions, str):
            self.required_permissions = [required_permissions]
        else:
            self.required_permissions = required_permissions

    async def __call__(self, current_user: AuthorToken = Depends(validate_token_header)):
        """
        Dependencia que verifica si el usuario autenticado tiene los permisos requeridos.
        El usuario se obtiene de la dependencia `validate_token_header`.
        """
        if not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario no tiene un rol asignado para verificar permisos."
            )
        
        # Extraer los nombres de los permisos del rol del usuario
        user_permissions_names = {p.name for p in current_user.role.permissions}
        
        # Verificar si el usuario tiene TODOS los permisos requeridos
        if not all(perm in user_permissions_names for perm in self.required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso(s) '{', '.join(self.required_permissions)}' requerido(s) para esta operación."
            )
        
        return current_user # Retorna el usuario si tiene el permiso