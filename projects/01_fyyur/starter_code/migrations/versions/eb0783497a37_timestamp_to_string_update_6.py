"""timestamp to string update 6

Revision ID: eb0783497a37
Revises: 8a6a6b8c9472
Create Date: 2020-05-03 21:06:33.198479

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'eb0783497a37'
down_revision = '8a6a6b8c9472'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Shows', 'start_time')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Shows', sa.Column('start_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###