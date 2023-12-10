"""empty message

Revision ID: ab43e9ad9d19
Revises: 1a541b65a8d5
Create Date: 2023-11-24 11:13:07.081706

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab43e9ad9d19'
down_revision = '1a541b65a8d5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.add_column(sa.Column('next_id', sa.Integer(), nullable=True))
        batch_op.drop_index('ix_message_timestamp')
        batch_op.drop_column('timestamp')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.add_column(sa.Column('timestamp', sa.DATETIME(), nullable=True))
        batch_op.create_index('ix_message_timestamp', ['timestamp'], unique=False)
        batch_op.drop_column('next_id')

    # ### end Alembic commands ###