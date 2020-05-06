"""empty message

Revision ID: a2d8424c27df
Revises: adb25c55a2f9
Create Date: 2020-05-06 18:05:33.460977

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2d8424c27df'
down_revision = 'adb25c55a2f9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
    op.add_column('venues', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('venues', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('venues', sa.Column('webiste', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'webiste')
    op.drop_column('venues', 'seeking_talent')
    op.drop_column('venues', 'seeking_description')
    op.drop_column('venues', 'genres')
    # ### end Alembic commands ###
