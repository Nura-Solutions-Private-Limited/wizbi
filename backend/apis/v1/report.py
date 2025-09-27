import os
from typing import List

import sqlalchemy as sa
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi_pagination import Page
from sqlalchemy.orm import Session

import constants
from apis.v1.login import get_current_user_from_token
from db.auth.dbconnection import DatabaseConnection
from db.models.models import Report, User
from db.session import get_db
from db.views.report import (
    all_reports_paginated,
    create_report,
    list_all_reports,
    list_report,
    list_reports_for_pipeline,
    show_excel_report,
    show_html_report,
    show_pdf_report,
    show_sql_query,
)
from schemas.report import CreateReport, ShowReport

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/reports/{pipeline_id}", response_model=ShowReport)
def create_reports(createReport: CreateReport,
                   db: Session = Depends(get_db),
                   user_id: User = Depends(get_current_user_from_token)):

    return create_report(createReport=createReport,
                         db=db,
                         user_id=user_id)


@router.get("/reports",
            response_model=List[ShowReport],
            deprecated=True)
def get_all_reports(db: Session = Depends(get_db),
                    report_type: str = Query("auto-generated",
                                             description="Report type (A/C)\
                                                \n Auto Generated(auto-generated)\
                                                \n Custom (custom_generated)", ),
                    current_user: User = Depends(get_current_user_from_token)):
    return list_all_reports(db=db,
                            user_id=current_user.id,
                            report_type=report_type)


@router.get("/reports-paginated",
            response_model=Page[ShowReport])
def get_all_paginated_reports(db: Session = Depends(get_db),
                              report_type: str = Query("auto-generated",
                              description="Report type (A/C)\
                                \n Auto Generated(auto-generated)\
                                \n Custom (custom_generated)", ),
                              current_user: User = Depends(get_current_user_from_token)):
    return all_reports_paginated(db=db,
                                 user_id=current_user.id,
                                 report_type=report_type)


@router.get("/reports-auto", response_model=List[ShowReport], deprecated=True)
def get_all_auto_reports(db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user_from_token)):
    report_type = "auto-generated"
    return list_all_reports(db=db,
                            user_id=current_user.id,
                            report_type=report_type)


@router.get("/reports-auto-paginated", response_model=List[ShowReport])
def get_all_paginated_auto_reports(db: Session = Depends(get_db),
                                   current_user: User = Depends(get_current_user_from_token)):
    report_type = "auto-generated"
    return all_reports_paginated(db=db,
                                 user_id=current_user.id,
                                 report_type=report_type)


@router.get("/reports-custom", response_model=List[ShowReport], deprecated=True)
def get_all_custom_reports(db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user_from_token)):
    report_type = "custom_generated"
    return list_all_reports(db=db,
                            user_id=current_user.id,
                            report_type=report_type)


@router.get("/reports-custom-paginated", response_model=List[ShowReport])
def get_all_paginated_custom_reports(db: Session = Depends(get_db),
                                     current_user: User = Depends(get_current_user_from_token)):
    report_type = "custom_generated"
    return all_reports_paginated(db=db,
                                 user_id=current_user.id,
                                 report_type=report_type)


@router.get("/reports/{pipeline_id}",
            response_model=List[ShowReport])
def get_reports_for_pipeline(pipeline_id: int,
                             db: Session = Depends(get_db),
                             report_type: str = Query("auto-generated",
                                                      description="Report type (A/C)\
                                                \n Auto Generated(auto-generated)\
                                                \n Custom(custom_generated)", ),
                             current_user: User = Depends(get_current_user_from_token),):
    return list_reports_for_pipeline(db=db,
                                     user_id=current_user.id,
                                     pipeline_id=pipeline_id,
                                     report_type=report_type)


@router.get("/reports-auto-pipeline/{pipeline_id}", response_model=List[ShowReport])
def get_reports_auto_for_pipeline(pipeline_id: int,
                                  db: Session = Depends(get_db),
                                  current_user: User = Depends(get_current_user_from_token),):
    report_type = "auto-generated"
    return list_reports_for_pipeline(db=db,
                                     user_id=current_user.id,
                                     pipeline_id=pipeline_id,
                                     report_type=report_type)


@router.get("/reports-custom-pipeline/{pipeline_id}", response_model=List[ShowReport])
def get_reports_cust_for_pipeline(pipeline_id: int,
                                  db: Session = Depends(get_db),
                                  current_user: User = Depends(get_current_user_from_token),):
    report_type = "custom_generated"
    return list_reports_for_pipeline(db=db,
                                     user_id=current_user.id,
                                     pipeline_id=pipeline_id,
                                     report_type=report_type)


@router.get("/reports/{report_id}", response_model=ShowReport)
def get_specific_report(report_id: int,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user_from_token)):
    return list_report(db=db, id=report_id, user_id=current_user.id)


@router.get("/showreport/{report_id}", response_class=FileResponse)
def gen_report(report_id: int,
               report_type: str = Query("H",
                                        description="Report output type (P/E/H/S)", ),
               db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user_from_token)):
    if report_type.upper() == 'P':
        return show_pdf_report(db=db, report_id=report_id, current_user=current_user)

    elif report_type.upper() == 'E':
        return show_excel_report(db=db, report_id=report_id, current_user=current_user)

    elif report_type.upper() == 'H':
        return show_html_report(db=db, report_id=report_id, current_user=current_user)

    elif report_type.upper() == 'S':
        return show_sql_query(db=db, report_id=report_id, current_user=current_user)


@router.get("/show_pdf_report/{report_id}", response_class=FileResponse)
def gen_pdf_report(report_id: int,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user_from_token)):
    return show_pdf_report(db=db, report_id=report_id, current_user=current_user)


@router.get("/show_excel_report/{report_id}", response_class=FileResponse)
def gen_excel_report(report_id: int,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user_from_token)):

    return show_excel_report(db=db, report_id=report_id, current_user=current_user)


@router.get("/show_html_report/{report_id}", response_class=FileResponse)
def gen_html_report(report_id: int,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user_from_token)):
    return show_html_report(db=db, report_id=report_id, current_user=current_user)


@router.get("/show_sql_report/{report_id}", response_class=FileResponse)
def gen_sql_report(report_id: int,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user_from_token)):
    return show_sql_query(db=db, report_id=report_id, current_user=current_user)
