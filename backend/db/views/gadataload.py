import itertools
import json
import os
import tempfile
from datetime import date, datetime, timedelta

import pandas as pd
import structlog
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

import constants
from db.views.job import add_update_job_status

logger = structlog.getLogger(__name__)


class GoogleAnalyticsDataLoad:
    def __init__(self, db, pipeline_id, ga_conn, dest_db_engine, dest_db_conn, connection_exts) -> None:
        self.db = db
        self.pipeline_id = pipeline_id
        self.ga_conn = ga_conn
        self.dest_db_engine = dest_db_engine
        self.dest_db_conn = dest_db_conn
        self.property_id = ga_conn.ga_property_id
        self.ga_auth_json = ga_conn.ga_auth_json
        self.connection_exts = connection_exts

        self.ga_day_data = constants.GA_DAY_DATA
        self.starting_date = "20daysAgo"
        self.ending_date = "1daysAgo"

        self.today = date.today()
        self.extracted_date = self.today - timedelta(3)

        self.auth_file = tempfile.NamedTemporaryFile(suffix=".json", mode="w+")
        json.dump(self.ga_auth_json, self.auth_file)
        self.auth_file.flush()
        logger.info(self.auth_file.name)

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.auth_file.name
        self.client = BetaAnalyticsDataClient()

    def query_data(self, api_response, dimension, ga_day):
        dimension_headers = [header.name for header in api_response.dimension_headers]
        metric_headers = [header.name for header in api_response.metric_headers]
        # metric_headers_dtype = [header.type_ for header in api_response.metric_headers]
        dimensions = []
        metrics = []
        for i in range(len(dimension_headers)):
            dimensions.append([row.dimension_values[i].value for row in api_response.rows])
        dimensions
        for i in range(len(metric_headers)):
            metrics.append([row.metric_values[i].value for row in api_response.rows])
        headers = dimension_headers, metric_headers
        headers = list(itertools.chain.from_iterable(headers))

        dfs = []

        # metric_dict = dict(zip(metric_headers, metric_headers_dtype))

        self.extracted_date = self.today - timedelta(ga_day)
        column_list = ["dimension", "dimension_value", "metric", "metric_value", "date"]
        for mh in metric_headers:
            tdf = pd.DataFrame()
            tdf["dimension_value"] = pd.Series(dimensions[0])
            tdf["dimension"] = dimension
            tdf["metric"] = mh
            tdf["metric_value"] = pd.to_numeric(pd.Series(metrics[metric_headers.index(mh)]), errors="coerce")
            tdf["date"] = self.extracted_date
            tdf = tdf[column_list]
            dfs.append(tdf)

        return pd.concat(dfs, ignore_index=True)

    def load_data_db(self, df, dimension):
        table_name = "google_analytics"
        df.to_sql(table_name, con=self.dest_db_engine, index=False, if_exists="append")

    def load_data(self, job_id):
        try:
            # connection_exts = self.db.query(Connection_Ext).filter(Connection_Ext.db_conn_id == self.ga_conn.id).all()
            # delete data if any loaded for the extracted day
            table_name = "google_analytics"
            try:
                table_exist_query = f"delete FROM {table_name} where date='{self.extracted_date}'"
                self.dest_db_engine.execute(table_exist_query)
            except Exception as ex:
                logger.info(f"google_analytics table does not exist:{ex}")

            for conn_ext in self.connection_exts:
                metric_list = []
                for metric in conn_ext.dimension_metric:
                    metric_list.append(f'[Metric(name="{metric}")]')

                dimension = conn_ext.dimension

                for ga_day in range(1, self.ga_day_data):
                    self.starting_date = f"{ga_day}daysAgo"
                    self.ending_date = f"{ga_day}daysAgo"
                    request_api = RunReportRequest(
                        property=f"properties/{self.property_id}",
                        dimensions=[Dimension(name=dimension)],
                        metrics=[Metric(name=i) for i in conn_ext.dimension_metric],
                        date_ranges=[DateRange(start_date=self.starting_date, end_date=self.ending_date)],
                    )
                    response = self.client.run_report(request_api)
                    final_data = self.query_data(response, dimension, ga_day)

                    self.load_data_db(final_data, dimension)

                    # Update job status to success
                    current_time = datetime.now()
                    job_status = "Success"
                    add_update_job_status(
                        self.db,
                        status=job_status,
                        job_id=job_id,
                        pipeline_id=self.pipeline_id,
                        job_date_time=current_time
                    )
        except Exception as ex:
            logger.error(f"Error in loading google analytics data: {ex}")
            current_time = datetime.now()
            job_status = "Completed with errors"
            add_update_job_status(
                self.db, status=job_status, job_id=job_id, pipeline_id=self.pipeline_id, job_date_time=current_time
            )
            raise Exception(f"Error in loading google analytics data: {ex}")
