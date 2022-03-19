import os
from datetime import datetime

import peewee as pw
from playhouse.postgres_ext import PostgresqlExtDatabase

# Init DB
db = PostgresqlExtDatabase(os.environ.get('DB_NAME', 'postgres'),
                           user=os.environ['DB_USER'],
                           password=os.environ['DB_PASSWORD'],
                           host=os.environ['DB_HOST'],
                           autoconnect=False)


class Term(pw.Model):
    """
    Term model.
    """

    created = pw.DateTimeField(default=datetime.utcnow)
    text = pw.CharField(unique=True, index=True)

    class Meta:
        database = db


with db.atomic():
    db.create_tables([Term])
