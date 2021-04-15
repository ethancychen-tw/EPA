"""empty message

Revision ID: a7437ffa0074
Revises: 
Create Date: 2021-04-15 23:48:58.110148

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7437ffa0074'
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
    op.create_table('location',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('desc', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('about_me', sa.String(length=120), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('is_activated', sa.Boolean(), nullable=True),
    sa.Column('lineid', sa.String(length=128), nullable=True),
    sa.Column('role', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    op.create_table('reviewee',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reviewer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tweet',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('review',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('location', sa.Integer(), nullable=True),
    sa.Column('epa', sa.Integer(), nullable=True),
    sa.Column('reviewee_id', sa.Integer(), nullable=True),
    sa.Column('reviewer_id', sa.Integer(), nullable=True),
    sa.Column('review_difficulty', sa.Integer(), nullable=True),
    sa.Column('review_compliment', sa.String(length=512), nullable=True),
    sa.Column('review_suggestion', sa.String(length=512), nullable=True),
    sa.Column('review_score', sa.Integer(), nullable=True),
    sa.Column('complete', sa.Boolean(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('last_edited', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['epa'], ['epa.id'], ),
    sa.ForeignKeyConstraint(['location'], ['location.id'], ),
    sa.ForeignKeyConstraint(['reviewee_id'], ['reviewee.id'], ),
    sa.ForeignKeyConstraint(['reviewer_id'], ['reviewer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('review')
    op.drop_table('tweet')
    op.drop_table('reviewer')
    op.drop_table('reviewee')
    op.drop_table('followers')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('location')
    op.drop_table('epa')
    # ### end Alembic commands ###