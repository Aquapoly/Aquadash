"""Constraints on threshold values

Revision ID: b99bff401293
Revises: 8975582390c7
Create Date: 2026-03-13 22:05:31.580716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b99bff401293'
down_revision: Union[str, Sequence[str], None] = '8975582390c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint("check_threshold_values", "sensors", 
            "threshold_critically_low <= threshold_low AND "
            "threshold_low <= threshold_high AND "
            "threshold_high <= threshold_critically_high")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("check_threshold_values", "sensors", type_="check")
