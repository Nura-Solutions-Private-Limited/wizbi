import time
from datetime import datetime

import pandas as pd
import structlog
import tweepy
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.models.models import Db_Conn, X_Conn
from db.views.job import add_update_job_status

logger = structlog.getLogger(__name__)


class XDataLoad:
    def __init__(self, db: Session,
                 pipeline_id: int,
                 source_db_conn: Db_Conn,
                 dest_db_conn: Db_Conn,
                 dest_db_engine=None):
        self.db = db
        self.pipeline_id = pipeline_id
        self.source_db_conn = source_db_conn
        self.dest_db_conn = dest_db_conn
        self.dest_db_engine = dest_db_engine

    def get_x_data(self) -> pd.DataFrame:
        '''
        This method will use the source connection to fetch the connection details of x
        and then using the details it will fetch the x data and return the data as dataframe
        '''
        if not self.source_db_conn:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Source connection not found")

        # Fetch x connection details
        x_conn = self.db.query(X_Conn).filter(X_Conn.db_conn_id == self.source_db_conn.id).first()
        if not x_conn:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="X connection not found")

        x_user_name = x_conn.user_name
        x_bearer_token = x_conn.bearer_token
        x_access_token = x_conn.access_token  # noqa: F841
        x_access_token_secret = x_conn.access_token_secret  # noqa: F841

        client = tweepy.Client(bearer_token=x_bearer_token)

        user_response = client.get_user(username=x_user_name)
        user_id_numeric = user_response.data.id

        MAX_RETRIES = 3
        RETRY_DELAY_SECONDS = 60  # Wait for 1 minute initially
        tweets_data = []
        for attempt in range(MAX_RETRIES):
            try:
                # get tweet analytics for last 10 tweets
                response = client.get_users_tweets(id=user_id_numeric, tweet_fields=["public_metrics", "created_at"], max_results=10)

                if response.data:
                    for tweet in response.data:
                        tweets_data.append({
                            "tweet_id": tweet.id,
                            "tweeter_username": x_user_name,
                            "created_at": tweet.created_at,
                            "likes": tweet.public_metrics['like_count'],
                            "retweets": tweet.public_metrics['retweet_count'],
                            "replies": tweet.public_metrics['reply_count'],
                            "impressions": tweet.public_metrics.get('impression_count', 'N/A')  # Use .get() for potentially missing keys
                        })
                        print(f"Tweet ID: {tweet.id}")
                        print(f"Tweeter Username: {x_user_name}")
                        print(f"Created At: {tweet.created_at}")
                        print(f"Likes: {tweet.public_metrics['like_count']}")
                        print(f"Retweets: {tweet.public_metrics['retweet_count']}")
                        print(f"Replies: {tweet.public_metrics['reply_count']}")
                        print(f"Impressions: {tweet.public_metrics.get('impression_count', 'N/A')}") # Use .get() for potentially missing keys
                        print("-" * 40)
                break  # Exit loop if successful
            except tweepy.TooManyRequests:
                logger.error(f"Rate limit exceeded. Waiting for {RETRY_DELAY_SECONDS * (attempt + 1)} seconds before retrying...")
                time.sleep(RETRY_DELAY_SECONDS * (attempt + 1))  # Exponential backoff could be better
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                break
        df = pd.DataFrame(tweets_data)
        return df

    def load_x_data(self, df: pd.DataFrame):
        table_name = 'x_tweet_data'
        df.to_sql(table_name, con=self.dest_db_engine, index=False, if_exists="append")

    def load_data(self, job_id: int):
        '''
        Read x data and load in table
        '''
        try:
            df = self.get_x_data()
            if not df.empty:
                self.load_x_data(df)
                logger.info("Data loaded successfully.")
            else:
                logger.warning("No data found to load.")

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
            return True
        except Exception as e:
            logger.error(f"Error in loading x data: {e}")
            current_time = datetime.now()
            job_status = "Completed with errors"
            add_update_job_status(
                self.db,
                status=job_status,
                job_id=job_id,
                pipeline_id=self.pipeline_id,
                job_date_time=current_time
            )
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
