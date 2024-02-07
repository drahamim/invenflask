"""empty message

Revision ID: 6cf6bb1af5e1
Revises: 
Create Date: 2024-02-04 16:49:01.576024

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6cf6bb1af5e1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assets', schema=None) as batch_op:
        batch_op.create_unique_constraint('asset_id', ['id'])

    with op.batch_alter_table('checkouts', schema=None) as batch_op:
        batch_op.create_unique_constraint('check_a_id', ['assetid'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('checkouts', schema=None) as batch_op:
        batch_op.drop_constraint('check_a_id', type_='unique')

    with op.batch_alter_table('assets', schema=None) as batch_op:
        batch_op.drop_constraint('asset_id', type_='unique')

    # ### end Alembic commands ###