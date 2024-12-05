"""first migration

Revision ID: ecba2f5b8b72
Revises: 
Create Date: 2024-11-29 13:20:52.640464

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ecba2f5b8b72'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('news',
    sa.Column('news_id', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('filename', sa.String(length=100), nullable=False),
    sa.Column('link', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('news_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('news')
    # ### end Alembic commands ###