"""empty message

Revision ID: a34c4754f81d
Revises: d79136b26f8e
Create Date: 2021-05-01 13:35:35.965584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a34c4754f81d'
down_revision = 'd79136b26f8e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('internal_group_id', sa.Integer(), nullable=True))
    op.drop_constraint('users_interal_group_id_fkey', 'users', type_='foreignkey')
    op.create_foreign_key(None, 'users', 'groups', ['internal_group_id'], ['id'])
    op.drop_column('users', 'interal_group_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('interal_group_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.create_foreign_key('users_interal_group_id_fkey', 'users', 'groups', ['interal_group_id'], ['id'])
    op.drop_column('users', 'internal_group_id')
    # ### end Alembic commands ###
