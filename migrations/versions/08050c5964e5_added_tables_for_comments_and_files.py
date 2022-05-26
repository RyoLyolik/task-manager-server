"""Added tables for comments and files

Revision ID: 08050c5964e5
Revises: 07342ab9c6e5
Create Date: 2022-05-26 13:47:18.816609

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08050c5964e5'
down_revision = '07342ab9c6e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comments',
    sa.Column('comment_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('comment_id', name=op.f('pk__comments'))
    )
    op.create_table('files',
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.task_id'], name=op.f('fk__files__task_id__tasks')),
    sa.PrimaryKeyConstraint('file_id', name=op.f('pk__files'))
    )
    op.drop_column('tasks', 'attachments')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('attachments', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_table('files')
    op.drop_table('comments')
    # ### end Alembic commands ###
