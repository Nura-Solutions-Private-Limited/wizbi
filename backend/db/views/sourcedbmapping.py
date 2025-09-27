from sqlalchemy.orm import Session

from db.models.models import Source_Db_Mapping
from schemas.sourcedbmapping import CreateSourceDbMapping


def create_new_source_db_mapping(createSourceDbMapping: CreateSourceDbMapping, db: Session):
    source_db_mapping = Source_Db_Mapping(db_conn_id=createSourceDbMapping.db_conn_id,
                                          table_column=createSourceDbMapping.table_column,
                                          is_attr=createSourceDbMapping.is_attr,
                                          is_measure=createSourceDbMapping.is_measure,
                                          is_attr_direct=createSourceDbMapping.is_attr_direct,
                                          attr_lookup_table=createSourceDbMapping.attr_lookup_table,
                                          attr_lookup_column=createSourceDbMapping.attr_lookup_column,
                                          time_lookup_table=createSourceDbMapping.time_lookup_table,
                                          time_lookup_key=createSourceDbMapping.time_lookup_key,
                                          time_column=createSourceDbMapping.time_column,
                                          measure_constant_value=createSourceDbMapping.measure_constant_value)

    db.add(source_db_mapping)
    db.commit()
    db.refresh(source_db_mapping)
    return source_db_mapping


def list_source_db_mapping(db: Session, id: int = None):
    if id:
        source_db_mapping = db.query(Source_Db_Mapping).filter(Source_Db_Mapping.id == id).first()
    else:
        source_db_mapping = db.query(Source_Db_Mapping).all()
    return source_db_mapping
