"""add msc_classes column to arxiv_paper

Revision ID: 73a6e35b6cee
Revises: 8bdaab87d45c
Create Date: 2021-04-23 13:49:23.272873

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73a6e35b6cee'
down_revision = '8bdaab87d45c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('arxiv_paper', sa.Column('msc_classes', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('arxiv_paper', 'msc_classes')
    # ### end Alembic commands ###
