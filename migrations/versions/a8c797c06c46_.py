"""empty message

Revision ID: a8c797c06c46
Revises: 0d63adb8c19d
Create Date: 2021-07-03 15:54:04.237874

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8c797c06c46'
down_revision = '0d63adb8c19d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('milestone_item', sa.Column('code', sa.String(length=16), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('milestone_item', 'code')
    # ### end Alembic commands ###
