import structlog
from sqlalchemy.orm import Session

from db.models.models import Tenant
from schemas.tenant import CreateTenant, UpdateTenant

logger = structlog.getLogger(__name__)


def create_tnt(createTenant: CreateTenant, db: Session, user_id: int):
    '''
    Create tenant
    '''
    try:
        tenant = Tenant(description=createTenant.description,
                        company_name=createTenant.company_name)

        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        return tenant

    except Exception as ex:
        logger.error(f"Error in creating tenant : {str(ex)}")
        raise ex


def update_tnt(updateTenant: UpdateTenant, db: Session, user_id: int, id: int):
    '''
    Update tenant
    '''
    tenant = db.query(Tenant).filter(Tenant.id == id).first()

    tenant.description = updateTenant.description
    tenant.company_name = updateTenant.company_name

    db.commit()
    db.refresh(tenant)
    return tenant


def list_tnts(db: Session, user_id: int):
    '''
    Get all the tenant
    '''
    try:
        tenant_list = list()

        tenants = db.query(Tenant).all()

        for tenant in tenants:
            tenant_list.append(tenant)

        return tenant_list

    except Exception as ex:
        logger.error(f"Error in getting all the tenants data : {str(ex)}")
        raise ex


def list_tnt(id: int, db: Session, user_id: int):
    '''
    Get a tenant by id
    '''
    try:
        tenant = db.query(Tenant).filter(Tenant.id == id).first()
        return tenant

    except Exception as ex:
        logger.error(f"Error in getting tenant data : {str(ex)}")
        raise ex


def delete_tnt(id: int, db: Session, user_id: int):
    '''
    delete tenant by id
    '''
    existing_tenant = db.query(Tenant).filter(Tenant.id == id)

    if not existing_tenant.first():
        return 0
    existing_tenant.delete(synchronize_session=False)
    db.commit()
    return 1
