"""empty message

Revision ID: 8d80516bfdcf
Revises: 
Create Date: 2021-05-08 22:45:21.218078

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8d80516bfdcf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('epa',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('desc', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('groups',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('desc', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_groups_name'), 'groups', ['name'], unique=True)
    op.create_table('line_new_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('line_userId', sa.String(length=64), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('line_userId')
    )
    op.create_table('location',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('desc', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('review_difficulty',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('desc', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('review_score',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('desc', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('review_source',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('desc', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('role',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('desc', sa.String(length=64), nullable=True),
    sa.Column('can_request_review', sa.Boolean(), nullable=True),
    sa.Column('can_create_and_edit_review', sa.Boolean(), nullable=True),
    sa.Column('is_manager', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('is_activated', sa.Boolean(), nullable=True),
    sa.Column('internal_group_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('line_userId', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['internal_group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('reviews',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.Column('epa_id', sa.Integer(), nullable=True),
    sa.Column('implement_date', sa.DateTime(), nullable=True),
    sa.Column('review_source_id', sa.Integer(), nullable=True),
    sa.Column('review_difficulty_id', sa.Integer(), nullable=True),
    sa.Column('review_score_id', sa.Integer(), nullable=True),
    sa.Column('reviewee_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('review_compliment', sa.String(length=512), nullable=True),
    sa.Column('review_suggestion', sa.String(length=512), nullable=True),
    sa.Column('complete', sa.Boolean(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('last_edited', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['epa_id'], ['epa.id'], ),
    sa.ForeignKeyConstraint(['location_id'], ['location.id'], ),
    sa.ForeignKeyConstraint(['review_difficulty_id'], ['review_difficulty.id'], ),
    sa.ForeignKeyConstraint(['review_score_id'], ['review_score.id'], ),
    sa.ForeignKeyConstraint(['review_source_id'], ['review_source.id'], ),
    sa.ForeignKeyConstraint(['reviewee_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_externalgroup',
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_externalgroup')
    op.drop_table('reviews')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('role')
    op.drop_table('review_source')
    op.drop_table('review_score')
    op.drop_table('review_difficulty')
    op.drop_table('location')
    op.drop_table('line_new_users')
    op.drop_index(op.f('ix_groups_name'), table_name='groups')
    op.drop_table('groups')
    op.drop_table('epa')
    # ### end Alembic commands ###