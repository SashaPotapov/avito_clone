"""empty message

Revision ID: ab3e9f0b4efe
Revises: f54ad86d7565
Create Date: 2021-06-21 22:24:10.865438

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab3e9f0b4efe'
down_revision = 'f54ad86d7565'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'name',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
    op.alter_column('users', 'address',
               existing_type=sa.TEXT(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'address',
               existing_type=sa.TEXT(),
               nullable=False)
    op.alter_column('users', 'name',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
    # ### end Alembic commands ###
