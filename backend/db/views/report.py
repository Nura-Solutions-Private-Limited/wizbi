
import os
from enum import Enum
from io import BytesIO
from typing import List, Union

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import structlog
import weasyprint
from fastapi import HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from matplotlib.backends.backend_pdf import PdfPages
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.utils.dataframe import dataframe_to_rows
from sqlalchemy import literal_column, select
from sqlalchemy.orm import Session

import constants
from db.auth.dbconnection import DatabaseConnection
from db.models.models import Db_Conn, Pipeline, Report
from db.views.permission_checker import PermissionChecker
from schemas.report import CreateReport

matplotlib.use("Agg")


logger = structlog.getLogger(__name__)


class ReportType(Enum):
    A = "auto-generated"
    C = "custom_generated"


def create_report(createReport: CreateReport, db: Session, user_id: int):
    try:
        report = Report(
            pipeline_id=createReport.pipeline_id,
            type=createReport.type,
            name=createReport.name,
            sql_query=createReport.sql_query,
            google_link=createReport.google_link,
            google_json=createReport.google_json,
        )

        db.add(report)
        db.commit()
        db.refresh(report)
        return report
    except Exception as ex:
        logger.error("Error in creating report :{}".format(str(ex)))
        raise ex


def list_all_reports(db: Session, user_id: int, report_type: str):
    """
    Get all reports along with pipeline data
    """
    try:
        permissionChecker = PermissionChecker()
        report_permission, report_ids = permissionChecker.get_permission(db=db,
                                                                         user_id=user_id,
                                                                         permission_for='reports')
        logger.info(f'Userid {user_id} Report permission {report_permission} and ids {report_ids}')

        report_list = list()

        if report_permission and not report_ids:
            reports = db.query(Report)\
                        .join(Pipeline, Report.pipeline_id == Pipeline.id)\
                        .filter(Report.type == report_type)\
                        .all()
        elif report_permission and report_ids:
            reports = db.query(Report)\
                        .join(Pipeline, Report.pipeline_id == Pipeline.id)\
                        .filter(Report.type == report_type)\
                        .filter(Report.id.in_(report_ids))\
                        .all()

        for report in reports:
            report_dict = report.__dict__

            # Get pipeline data using pipeline id and append it to audit resultset
            pipeline_id = report.pipeline_id
            pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
            pipeline_dict = pipeline.__dict__
            # pipeline_dict.pop('_sa_instance_state')
            report_dict["pipeline"] = pipeline_dict
            report_list.append(report_dict)

        return report_list
    except Exception as ex:
        logger.error("Error in getting reports data :{}".format(str(ex)))
        raise ex


def all_reports_paginated(db: Session, user_id: int, report_type: str):
    """
    Get all reports along with pipeline data
    """
    try:
        permissionChecker = PermissionChecker()
        report_permission, report_ids = permissionChecker.get_permission(db=db,
                                                                         user_id=user_id,
                                                                         permission_for='reports')
        logger.info(f'Userid {user_id} Report permission {report_permission} and ids {report_ids}')

        report_query = select(Report.id,
                              Report.pipeline_id,
                              Report.type,
                              Report.name,
                              Report.sql_query,
                              Report.google_link,
                              Report.google_json,
                              literal_column("NULL").label("pipeline")
                              ).join(Pipeline,
                                     Report.pipeline_id == Pipeline.id
                                     ).filter(Report.type == report_type)

        if report_permission and report_ids:
            report_query = report_query.filter(Report.id.in_(report_ids))
            # reports = db.query(Report)\
            #             .join(Pipeline, Report.pipeline_id == Pipeline.id)\
            #             .filter(Report.type == report_type)\
            #             .filter(Report.id.in_(report_ids))\
            #             .all()

        def pipeline_transformer(report):
            report_list = []
            for rep in report:
                rep = rep._asdict()
                pipeline_id = rep.get('pipeline_id')
                pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
                pipeline_dict = pipeline.__dict__
                rep["pipeline"] = pipeline_dict
                report_list.append(rep)
            return report_list

        report_list = paginate(db, query=report_query, transformer=pipeline_transformer)

        return report_list
    except Exception as ex:
        logger.error("Error in getting reports data :{}".format(str(ex)))
        raise ex


def list_reports_for_pipeline(db: Session, user_id: int, pipeline_id: int, report_type: str):
    """
    Get reports for a specific pipeline along with pipeline data
    """
    try:
        permissionChecker = PermissionChecker()
        report_permission, report_ids = permissionChecker.get_permission(db=db,
                                                                         user_id=user_id,
                                                                         permission_for='reports')
        logger.info(f'Userid {user_id} Report permission {report_permission} and ids {report_ids}')

        report_list = list()

        if report_permission and not report_ids:
            reports = db.query(Report)\
                        .join(Pipeline, Report.pipeline_id == Pipeline.id)\
                        .filter(Pipeline.id == pipeline_id)\
                        .filter(Report.type == report_type)\
                        .all()
        elif report_permission and report_ids:
            reports = db.query(Report)\
                        .join(Pipeline, Report.pipeline_id == Pipeline.id)\
                        .filter(Pipeline.id == pipeline_id)\
                        .filter(Report.type == report_type)\
                        .filter(Report.id.in_(report_ids))\
                        .all()

        for report in reports:
            report_dict = report.__dict__

            # Get pipeline data using pipeline id and append it to audit resultset
            pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
            pipeline_dict = pipeline.__dict__
            report_dict["pipeline"] = pipeline_dict
            report_list.append(report_dict)

        return report_list
    except Exception as ex:
        logger.error("Error in getting reports data :{}".format(str(ex)))
        raise ex


def list_report(db: Session, user_id: int, id: int = None):
    """
    Get report along with pipeline data
    """
    # report = db.query(Report).filter(Report.id == id).first()

    permissionChecker = PermissionChecker()
    report_permission, report_ids = permissionChecker.get_permission(db=db,
                                                                     user_id=user_id,
                                                                     permission_for='reports')
    logger.info(f'Userid {user_id} Report permission {report_permission} and ids {report_ids}')

    if report_permission and not report_ids:
        report = db.query(Report)\
                   .join(Pipeline, Report.pipeline_id == Pipeline.id)\
                   .filter(Pipeline.user_id == user_id)\
                   .filter(Report.id == id)\
                   .first()
    elif report_permission and report_ids:
        report = db.query(Report)\
                   .join(Pipeline, Report.pipeline_id == Pipeline.id)\
                   .filter(Pipeline.user_id == user_id)\
                   .filter(Report.id == id)\
                   .filter(Report.id.in_(report_ids))\
                   .first()

    if report:
        report_dict = report.__dict__

        # Get pipeline data using pipeline id and append it to audit resultset
        pipeline_id = report.pipeline_id
        pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
        pipeline_dict = pipeline.__dict__
        # pipeline_dict.pop('_sa_instance_state')
        report_dict["pipeline"] = pipeline_dict

        return report_dict
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")


def generate_html_content(report_name, chart_data, column1, column2):
    # Generate a list of colors for each bar
    bar_colors = ["red", "blue", "green", "orange", "purple"]

    # Construct the chart data with the color attribute for each bar
    chart_data_with_colors = []  # Start with an empty data row for column headers
    for i, data_row in enumerate(chart_data[1:], start=1):  # Skip the column header row
        color = bar_colors[i % len(bar_colors)]
        chart_data_with_colors.append([data_row[0], data_row[1], color])

    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>Google Bar Chart</title>
        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
        <script type="text/javascript">
            google.charts.load('current', {{packages: ['corechart']}});
            google.charts.setOnLoadCallback(drawChart);

            function drawChart() {{
                var data = new google.visualization.DataTable();
                data.addColumn('string', '{column1.title()}');
                data.addColumn('number', '{column2.title()}');
                data.addColumn({{type: 'string', role: 'style'}});
                data.addRows({chart_data_with_colors});

                var options = {{
                    title: '{report_name}',
                    hAxis: {{ title: '{column1.title()}', format: '####',slantedText: true, slantedTextAngle: 45 }},
                    vAxis: {{ title: '{column2.title()}' }},
                    legend: {{ position: 'right' }},
                    seriesType: 'bars'
                }};

                var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
                chart.draw(data, options);
            }}
        </script>
        </head>
        <body>
        <div id="chart_div" style="width: 1200px; height: 800px;"></div>
        </body>
        </html>
    """
    return html_content


def to_html_pretty(df, filename, title):
    """
    Write an entire dataframe to an HTML file
    with nice formatting.
    Thanks to @stackoverflowuser2010 for the
    pretty printer see https://stackoverflow.com/a/47723330/362951
    """
    ht = ""
    if title != "":
        ht += "<h2> %s </h2>\n" % title
    ht += df.to_html(classes="wide", escape=False)

    HTML_TEMPLATE1 = """
    <html>
    <head>
    <style>
    h2 {
        text-align: center;
        font-family: Helvetica, Arial, sans-serif;
    }
    table {
        margin-left: auto;
        margin-right: auto;
    }
    table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
    }
    th, td {
        padding: 5px;
        text-align: center;
        font-family: Helvetica, Arial, sans-serif;
        font-size: 90%;
    }
    table thead th {
        background-color: #6d6c6c; /* Dark grey background for column headers */
        color: #fff; /* White text for column headers */
    }
    table tbody tr:nth-child(odd) {
        background-color: #ffffff; /* dark background for odd rows */
    }
    table tbody tr:nth-child(even) {
        background-color: #f2f2f2; /* light background for even rows */
    }
    table tbody tr:hover {
        background-color: #dddddd;
    }
    .wide {
        width: 90%;
    }
    </style>
    </head>
    <body>
    """

    HTML_TEMPLATE2 = """
    </body>
    </html>
    """
    with open(filename, "w") as f:
        f.write(HTML_TEMPLATE1 + ht + HTML_TEMPLATE2)


def show_html_report(db: Session, report_id: int, current_user: int) -> Union[FileResponse, None]:
    report = db.query(Report).filter(Report.id == report_id).first()
    pipeline_id = report.pipeline_id
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    dest_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_dest_id).first()
    # Create target database connection
    targetdbcon = DatabaseConnection(
        database_type=dest_db_conn.db_type,
        username=dest_db_conn.db_username,
        password=dest_db_conn.db_password,
        host=dest_db_conn.db_host,
        port=dest_db_conn.db_port,
        schemas=pipeline.dest_schema_name,
    )
    target_engine = targetdbcon.get_engine()

    if report:
        query = report.sql_query
        title = report.name
        rows = pd.read_sql_query(query, target_engine)
        file_path = os.path.join(os.path.join(os.getcwd(), constants.REPORT_PATH), f"report{report_id}.html")
        if report.type == "auto-generated":
            column1 = title.split(" ")[-1]
            column2 = title.split(" ")[3]
            if not isinstance(rows, pd.DataFrame):
                raise ValueError("Invalid 'rows' data type. Expected pandas DataFrame.")
            # Prepare the data for the chart
            chart_data = [[column1, column2]]
            for index, row in rows.iterrows():
                second_value = int(row[-2]) if not pd.isna(row[-2]) else 0
                chart_data.append([row[0], second_value])

            # Generate the HTML content
            html_content = generate_html_content(title, chart_data, column1, column2)

            # Write the HTML content to a file

            with open(file_path, "w") as file:
                file.write(html_content)
        else:
            to_html_pretty(rows, file_path, title)

        return FileResponse(path=file_path, filename=f"report{report_id}.html", media_type="text/html")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")


def show_excel_report(db: Session, report_id: int, current_user: int) -> Union[FileResponse, None]:
    report = db.query(Report).filter(Report.id == report_id).first()
    if report:
        query = report.sql_query
        title = report.name
        result = db.execute(query)
        rows = result.fetchall()
        # Assuming that result.keys() contains the column names
        column_names = result.keys()

        # Create a DataFrame from the fetched data
        df = pd.DataFrame(rows, columns=column_names)
        wb = Workbook()
        ws = wb.active
        ws.title = "Report"
        for row in dataframe_to_rows(df, index=False, header=True):
            ws.append(row)

        if report.type == "auto-generated":
            # Create a Workbook and add a worksheet

            # Populate the worksheet with the data

            # Add a bar chart to the worksheet
            chart = BarChart()
            chart.title = title
            column_names = list(result.keys())
            chart.x_axis.title = column_names[0]
            chart.y_axis.title = column_names[-2]
            chart.style = 10
            chart.width = 15
            chart.height = 10
            chart.legend = None

            data_range = Reference(ws, min_col=2, min_row=1, max_col=len(result.keys()), max_row=len(rows) + 1)
            chart.add_data(data_range, titles_from_data=True)

            chart_location = f"E{len(rows) + 3}"  # Place the chart below the data
            ws.add_chart(chart, chart_location)

        file_path = os.path.join(os.path.join(os.getcwd(), constants.REPORT_PATH), f"report{report_id}.xlsx")
        # file_path = os.path.join(constants.REPORT_PATH, f"report{report_id}.html")
        wb.save(file_path)

        return FileResponse(
            path=file_path,
            filename=f"report{report_id}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")


def generate_pdf_table(df, title, filename):
    intermediate_html = "/tmp/intermediate.html"
    to_html_pretty(df, intermediate_html, title)
    """  soup = BeautifulSoup(intermediate_html, 'html.parser')

    # Measure the width and height of the HTML content
    html_width_mm = int(soup.body['width'].strip('px'))
    if 'width' in soup.body.attrs else 210  # Default to A4 width

    html_height_mm = int(soup.body['height'].strip('px'))
    if 'height' in soup.body.attrs else 297  # Default to A4 height

    # Create a page style with the measured dimensions
    page_style = {'size': (html_width_mm, html_height_mm)}
    """

    # Convert the html file to a pdf file using weasyprint
    weasyprint.HTML(intermediate_html).write_pdf(filename)


def generate_pdf_from_chart(chart_data, title, column1, column2):
    # Calculate the number of bars and set a suitable figure size
    num_bars = len(chart_data) - 1
    # max_fig_width = 1600  # Maximum width in pixels
    # bar_width = num_bars * 0.3 + 5

    figsize = (num_bars * 0.5 + 5, 6)  # Adjust as needed
    # figsize = (min(bar_width, max_fig_width / 100, num_bars), 6)  # Adjust as needed

    # Create a bar chart using matplotlib
    fig, ax = plt.subplots(figsize=figsize)
    # Create a color map with enough distinct colors
    # color_map = plt.get_cmap("tab20c")
    # bars = ax.bar([data[0] for data in chart_data[1:]], [data[1] for data in chart_data[1:]],
    # color=color_map(range(num_bars)))
    colors = plt.cm.get_cmap("tab20c", num_bars)

    _ = ax.bar(
        [data[0] for data in chart_data[1:]], [data[1] for data in chart_data[1:]], color=colors(range(num_bars))
    )

    # Set chart title and axis labels
    ax.set_title(title)
    ax.set_xlabel(column1)
    ax.set_ylabel(column2)

    # Rotate x-axis labels if necessary
    plt.xticks(rotation=45, ha="right")

    # Adjust layout to fit the labels and save space
    plt.tight_layout()

    # Create a PDF buffer to save the chart
    pdf_buffer = BytesIO()
    pdf_pages = PdfPages(pdf_buffer)
    pdf_pages.savefig(fig, bbox_inches="tight")
    pdf_pages.close()

    # Reset the buffer position before creating the FileResponse
    pdf_buffer.seek(0)
    return pdf_buffer


def show_pdf_report(db: Session, report_id: int, current_user: int) -> Union[FileResponse, None]:
    report = db.query(Report).filter(Report.id == report_id).first()
    pipeline_id = report.pipeline_id
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    dest_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_dest_id).first()
    # Create target database connection
    targetdbcon = DatabaseConnection(
        database_type=dest_db_conn.db_type,
        username=dest_db_conn.db_username,
        password=dest_db_conn.db_password,
        host=dest_db_conn.db_host,
        port=dest_db_conn.db_port,
        schemas=pipeline.dest_schema_name,
    )
    target_engine = targetdbcon.get_engine()

    if report:
        query = report.sql_query
        title = report.name
        rows = pd.read_sql_query(query, target_engine)
        # drop empty columns
        # rows = rows.dropna(axis=1, how='all')

        pdf_path = os.path.join(os.path.join(os.getcwd(), constants.REPORT_PATH), f"report{report_id}.pdf")
        if report.type == "auto-generated":
            column1 = title.split(" ")[-1]
            column2 = title.split(" ")[3]
            if not isinstance(rows, pd.DataFrame):
                raise ValueError("Invalid 'rows' data type. Expected pandas DataFrame.")
            # Prepare the data for the chart
            chart_data = [[column1, column2]]
            for index, row in rows.iterrows():
                second_value = int(row[-2]) if not pd.isna(row[-2]) else 0
                chart_data.append([row[0], second_value])
            pdf_buffer = generate_pdf_from_chart(chart_data, title, column1, column2)
            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(pdf_buffer.read())

            # Reset the buffer position before creating the FileResponse
            pdf_buffer.seek(0)
        else:
            # Convert the DataFrame to a list of dictionaries
            generate_pdf_table(rows, title, pdf_path)

        # Write the PDF buffer content to a file

        return FileResponse(path=pdf_path, filename=f"report{report_id}.pdf", media_type="application/pdf")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")


def show_sql_query(db: Session, report_id: int, current_user: int) -> Union[FileResponse, None]:
    report = db.query(Report).filter(Report.id == report_id).first()
    pipeline_id = report.pipeline_id
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    dest_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_dest_id).first()
    # Create target database connection
    targetdbcon = DatabaseConnection(
        database_type=dest_db_conn.db_type,
        username=dest_db_conn.db_username,
        password=dest_db_conn.db_password,
        host=dest_db_conn.db_host,
        port=dest_db_conn.db_port,
        schemas=pipeline.dest_schema_name,
    )
    _ = targetdbcon.get_engine()

    if report:
        query = report.sql_query
        file_path = os.path.join(os.path.join(os.getcwd(), constants.REPORT_PATH), f"report{report_id}.sql")
        with open(file_path, "w") as file:
            file.write(query)

        return FileResponse(path=file_path, filename=f"report{report_id}.sql", media_type="text/sql")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
