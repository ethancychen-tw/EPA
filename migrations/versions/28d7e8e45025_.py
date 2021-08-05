"""empty message

Revision ID: 28d7e8e45025
Revises: ab0b15e590ce
Create Date: 2021-08-06 01:23:16.664378

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '28d7e8e45025'
down_revision = 'ab0b15e590ce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('line_new_users')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('line_new_users',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('line_userId', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('create_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='line_new_users_pkey')
    )
    # ### end Alembic commands ###
