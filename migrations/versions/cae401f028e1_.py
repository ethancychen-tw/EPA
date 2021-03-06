"""empty message

Revision ID: cae401f028e1
Revises: c3522b6acfcc
Create Date: 2021-07-17 14:20:04.301089

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cae401f028e1'
down_revision = 'c3522b6acfcc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reviews', sa.Column('creator_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('reviews', sa.Column('is_draft', sa.Boolean(), nullable=True))
    op.add_column('reviews', sa.Column('complete', sa.Boolean(), nullable=True))
    op.create_foreign_key(None, 'reviews', 'users', ['creator_id'], ['id'])
    op.drop_column('reviews', 'status_complete')
    op.drop_column('reviews', 'status_draft')
    op.add_column('role', sa.Column('can_create_review', sa.Boolean(), nullable=True))
    op.add_column('role', sa.Column('can_edit_unfin_review', sa.Boolean(), nullable=True))
    op.add_column('role', sa.Column('can_delete_unfin_review', sa.Boolean(), nullable=True))
    op.drop_column('role', 'can_create_and_edit_review')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('role', sa.Column('can_create_and_edit_review', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('role', 'can_delete_unfin_review')
    op.drop_column('role', 'can_edit_unfin_review')
    op.drop_column('role', 'can_create_review')
    op.add_column('reviews', sa.Column('status_draft', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('reviews', sa.Column('status_complete', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'reviews', type_='foreignkey')
    op.drop_column('reviews', 'complete')
    op.drop_column('reviews', 'is_draft')
    op.drop_column('reviews', 'creator_id')
    # ### end Alembic commands ###
