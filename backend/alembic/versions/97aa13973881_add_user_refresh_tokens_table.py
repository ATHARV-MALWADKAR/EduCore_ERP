"""add_user_refresh_tokens_table

Revision ID: 97aa13973881
Revises: a26314ee01ab
Create Date: 2026-09-17 21:45:26.221737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97aa13973881'
down_revision: Union[str, Sequence[str], None] = 'a26314ee01ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user_refresh_tokens',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token_hash', sa.String(length=255), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('revoked_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token_hash')
    )
    op.create_index('idx_refresh_token_user_id', 'user_refresh_tokens', ['user_id'], unique=False)
    op.create_index('idx_refresh_token_expires', 'user_refresh_tokens', ['expires_at'], unique=False)


def downgrade() -> None:
    op.drop_table('user_refresh_tokens')
