"""empty message

Revision ID: 3a3239533401
Revises: ab3e9f0b4efe
Create Date: 2021-07-01 20:34:53.411327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a3239533401'
down_revision = 'ab3e9f0b4efe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('avatar_link', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'avatar_link')
    # ### end Alembic commands ###
