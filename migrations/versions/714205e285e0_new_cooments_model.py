"""New Cooments model

Revision ID: 714205e285e0
Revises: ddee86de31ee
Create Date: 2021-07-09 11:16:52.386001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '714205e285e0'
down_revision = 'ddee86de31ee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('product_id', sa.Integer(), nullable=True))
    op.drop_index('ix_comment_news_id', table_name='comment')
    op.create_index(op.f('ix_comment_product_id'), 'comment', ['product_id'], unique=False)
    op.drop_constraint('comment_news_id_fkey', 'comment', type_='foreignkey')
    op.create_foreign_key(None, 'comment', 'products', ['product_id'], ['id'], ondelete='CASCADE')
    op.drop_column('comment', 'news_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('news_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.create_foreign_key('comment_news_id_fkey', 'comment', 'products', ['news_id'], ['id'], ondelete='CASCADE')
    op.drop_index(op.f('ix_comment_product_id'), table_name='comment')
    op.create_index('ix_comment_news_id', 'comment', ['news_id'], unique=False)
    op.drop_column('comment', 'product_id')
    # ### end Alembic commands ###
