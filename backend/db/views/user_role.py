import structlog
from sqlalchemy.orm import Session

from db.models.models import UserRole
from schemas.user_role import AddUpdateUserRole, CreateUserRole, UpdateUserRole

logger = structlog.getLogger(__name__)



def create_user_rol(createUserRole: CreateUserRole, db: Session, user_id: int):
    '''
    Create user role
    '''
    try:
        user_role = UserRole(user_id = createUserRole.user_id,
                             role_id = createUserRole.role_id)
        
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        return user_role
    
    except Exception as ex:
        logger.error(f"Error in creating user role : {str(ex)}")
        raise ex
    

def add_update_user_rol(addUpdateUserRole: AddUpdateUserRole, db:Session, user_id: int):
    '''
    To add update user roles
    '''
    count = 0
    for user_roles in addUpdateUserRole:
        for role in user_roles.roles:

            userid = user_roles.user_id
            role_id = role.role_id

            # delete only once at the start (using count for that)
            if count == 0:
                existing_user_role = db.query(UserRole).filter(UserRole.user_id == userid)
                existing_user_role.delete(synchronize_session=False)
                db.commit()

            # add/ update
            try:
                user_role = UserRole(user_id = userid,
                                    role_id = role_id)
                db.add(user_role)
                db.commit()
                db.refresh(user_role)
            
            except Exception as ex:
                logger.error(f"Error in adding/ updating user role : {str(ex)}")
                raise ex
            
            count += 1
    return addUpdateUserRole

    

def update_user_rol(updateUserRole: UpdateUserRole, db: Session, user_id: int, id: int):
    '''
    Update user role
    '''
    user_role = db.query(UserRole).filter(UserRole.id == id).first()

    user_role.user_id = updateUserRole.user_id
    user_role.role_id = updateUserRole.role_id

    db.commit()
    db.refresh(user_role)
    return user_role


    

def list_user_rols(db:Session, user_id: int):
    '''
    Get all the user roles
    '''
    try:
        user_role_list = list()

        user_roles = db.query(UserRole).all()

        for user_role in user_roles:
            user_role_list.append(user_role)

        return user_role_list
    
    except Exception as ex:
        logger.error(f"Error in getting all the user role data : {str(ex)}")
        raise ex
    

def list_user_rol(id: int, db: Session, user_id: int):
    '''
    Get a user role by id
    '''
    try:
        user_role = db.query(UserRole).filter(UserRole.id == id).first()
        return user_role
    
    except Exception as ex:
        logger.error(f"Error in getting user role data : {str(ex)}")
        raise ex
    

def delete_user_rol(id: int, db: Session, user_id: int):
    '''
    delete user role by id
    '''
    existing_user_role = db.query(UserRole).filter(UserRole.id == id)

    if not existing_user_role.first():
        return 0
    existing_user_role.delete(synchronize_session=False)
    db.commit()
    return 1