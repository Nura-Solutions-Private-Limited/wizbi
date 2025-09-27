
import argparse
import re
from pathlib import Path
from uuid import UUID

import sqlalchemy as sa
import structlog
from alembic import command
from alembic.config import Config

from core.config import settings
from db.models.models import Permissions, Role, User, UserRole
from db.session import get_db

logger = structlog.getLogger(__name__)


class AppDB:
    def __init__(self):
        self.data = {}

    def upgrade_db_on_start(self):
        self.alembic_upgrade_head(settings.DB_DB)

    def downgrade_db_on_start(self):
        pass

    def create_user_on_start(self):
        pass
        # create user
        # create role
        # create user_role mapping
        # create permissions

    def create_schema(self, schema: str, url: str = None):
        logger.info("START create schema: " + schema)
        # try:
        #     with with_db("public") as db:
        #         db.execute(sa.schema.CreateSchema(schema))
        #         db.commit()
        # except Exception as e:
        #     logger.error(e)
        #     capture_exception(e)
        # logger.info("Done create schema: " + schema)

    # @timer
    def alembic_upgrade_head(self, schema_name: str, revision="head", url: str = None):
        logger.info("🔺 [Schema upgrade] " + schema_name + " to version: " + revision)
        # set the paths values

        if url is None:
            url = str(settings.DATABASE_URL)
            # url = "mysql://root:password@localhost:3306/wizbi_test"
        try:
            # create Alembic config and feed it with paths

            # mysql migration path
            MYSQL_MIGRATION_PATH = Path.joinpath(settings.PROJECT_DIR, "migrations", "databases", "mysql")

            config = Config(str(settings.PROJECT_DIR / "alembic.ini"))
            config.set_main_option("script_location", str(MYSQL_MIGRATION_PATH))
            config.set_main_option("sqlalchemy.url", url)
            config.cmd_opts = argparse.Namespace()  # arguments stub

            # If it is required to pass -x parameters to alembic
            x_arg = "".join(["tenant=", schema_name])  # "dry_run=" + "True"
            if not hasattr(config.cmd_opts, "x"):
                if x_arg is not None:
                    config.cmd_opts.x = []
                    if isinstance(x_arg, list) or isinstance(x_arg, tuple):
                        for x in x_arg:
                            config.cmd_opts.x.append(x)
                    else:
                        config.cmd_opts.x.append(x_arg)
                else:
                    config.cmd_opts.x = None

            # prepare and run the command
            revision = revision
            sql = False
            tag = None
            # command.stamp(config, revision, sql=sql, tag=tag)

            # upgrade command
            command.upgrade(config, revision, sql=sql, tag=tag)
        except Exception as e:
            logger.error(e)
            # capture_exception(e)
            # print(traceback.format_exc())

        logger.info("✅ Schema upgraded for: " + schema_name + " to version: " + revision)
