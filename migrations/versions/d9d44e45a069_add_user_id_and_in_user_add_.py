"""Add user_id and in user add relationship with task

Revision ID: d9d44e45a069
Revises: 
Create Date: 2024-12-09 16:54:31.308651

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9d44e45a069'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('tasks', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'tasks', 'user', ['user_id'], ['id'])

def downgrade():
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'user_id')
    # ### end Alembic commands ###
