import os
from argparse import Namespace

from alembic import command
from alembic.config import Config
from sqlalchemy import text
# from sqlalchemy_searchable import make_searchable
from extensions.sqlalchemy import SqlBaseModel, SessionLocal
from modules import *
from project_helpers.db_utils import functions
from project_helpers.config import postgres

target_metadata = SqlBaseModel.metadata
# make_searchable(metadata=SqlBaseModel.metadata, options={"regconfig": "pg_catalog.simple"})
alembicConfig = Config(
    "extensions/migrations/alembic.ini",
    cmd_opts=Namespace(autogenerate=True, ignore_unknown_revisions=True, x=None),
)
session = SessionLocal()
session.execute(text("DROP TABLE IF EXISTS alembic_version;"))

functions.create_search_functions(session)

session.commit()
alembicConfig.set_main_option("sqlalchemy.url", postgres.uri())
alembicConfig.set_main_option("script_location", "extensions/migrations")
isExist = os.path.exists("extensions/migrations/versions")
if not isExist:
    os.makedirs("extensions/migrations/versions")
command.stamp(alembicConfig, revision="head")
command.revision(alembicConfig, autogenerate=True)
command.upgrade(alembicConfig, revision="head")
command.stamp(alembicConfig, revision="head")
#
# insert_default_sections(session)
# insert_default_registry(session)
# insert_default_category(session)

session.close()
exit(0)
