from typing import List

import structlog
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.models.models import User_Group
from schemas.user_group import AddUpdateUserGroup, CreateUserGroup, UpdateUserGroup

logger = structlog.getLogger(__name__)



# def create_user_grp(createUserGroup: CreateUserGroup, db: Session, user_id: int):
#     '''
#     Create a user group
#     '''
#     try:
#         exiting_user_id = db.query(User_Group).filter(User_Group.user_id == createUserGroup.user_id).first()
#         exiting_group_id = db.query(User_Group).filter(User_Group.group_id == createUserGroup.group_id).first()

#         if exiting_user_id and exiting_group_id:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                                 detail="user group with same user id exist")
#         else:
#             user_group = User_Group(user_id = createUserGroup.user_id,
#                                 group_id = createUserGroup.group_id)
            
            
#             db.add(user_group)
#             db.commit()
#             db.refresh(user_group)
#             return user_group
    
#     except Exception as ex:
#         logger.error(f"Error in creating user group : {str(ex)}")
#         raise ex
    

def add_update_user_grp(addUpdateUserGroup: AddUpdateUserGroup, db: Session, user_id: int):
    '''
    Update User group
    '''

    count = 0
    for user_groups in addUpdateUserGroup:
        for group in user_groups.groups:

            userid = user_groups.user_id
            group_id = group.group_id

            # delete only once at the start (using count for that)
            if count == 0:
                existing_user_group = db.query(User_Group).filter(User_Group.user_id == userid)
                existing_user_group.delete(synchronize_session=False)
                db.commit()

            # add/ update
            try:
                user_group = User_Group(user_id = userid,
                                    group_id = group_id)
                db.add(user_group)
                db.commit()
                db.refresh(user_group)
            
            except Exception as ex:
                logger.error(f"Error in adding/ updating user group : {str(ex)}")
                raise ex
            
            count += 1
    return addUpdateUserGroup

        # user_groups_list = []
        # for ukey, uvalue in user_groups.items():
        #     if ukey == 'user_id':
        #         userid = uvalue
        #         existing_user_group = db.query(User_Group).filter(User_Group.user_id == userid)
        #         existing_user_group.delete(synchronize_session=False)
        #         db.commit()
        #     if ukey == 'groups':
        #         for v in uvalue:
        #             for key, value in v.items():
        #                 if key == 'group_id':
        #                     group_id = value
        #                     user_groups_list.append([userid, group_id])

        #                     try:
        #                         user_group = User_Group(user_id = userid,
        #                                             group_id = group_id)
        #                         db.add(user_group)
        #                         db.commit()
        #                         db.refresh(user_group)
        #                         # return user_group
                            
        #                     except Exception as ex:
        #                         logger.error(f"Error in adding/ updating user group : {str(ex)}")
        #                         raise ex


def list_user_grps(db:Session, user_id: int):
    '''
    Get all the user groups
    '''
    try:
        user_group_list = list()

        user_groups = db.query(User_Group).all()

        for user_group in user_groups:
            user_group_list.append(user_group)

        return user_group_list
    
    except Exception as ex:
        logger.error(f"Error in getting all the user group data : {str(ex)}")
        raise ex
    

def list_user_grp(id: int, db: Session, user_id: int):
    '''
    Get a user_group by id
    '''
    try:
        user_group = db.query(User_Group).filter(User_Group.id == id).first()
        return user_group
    
    except Exception as ex:
        logger.error(f"Error in getting user group data : {str(ex)}")
        raise ex
    

# def delete_user_grp(id: int, db: Session, user_id: int):
#     '''
#     delete user group by id
#     '''
#     existing_user_group = db.query(User_Group).filter(User_Group.id == id)

#     if not existing_user_group.first():
#         return 0
#     existing_user_group.delete(synchronize_session=False)
#     db.commit()
#     return 1