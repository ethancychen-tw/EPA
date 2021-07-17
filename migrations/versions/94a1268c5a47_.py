"""empty message

Revision ID: 94a1268c5a47
Revises: 66aef658993e
Create Date: 2021-07-17 21:25:23.054204

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94a1268c5a47'
down_revision = '66aef658993e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('role', sa.Column('can_be_reviewee', sa.Boolean(), nullable=True))
    op.add_column('role', sa.Column('can_be_reviewer', sa.Boolean(), nullable=True))
    op.drop_column('role', 'can_make_review')
    op.drop_column('role', 'can_be_review')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('role', sa.Column('can_be_review', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('role', sa.Column('can_make_review', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('role', 'can_be_reviewer')
    op.drop_column('role', 'can_be_reviewee')
    # ### end Alembic commands ###
