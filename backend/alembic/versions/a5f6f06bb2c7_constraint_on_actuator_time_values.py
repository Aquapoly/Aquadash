"""constraint on actuator time values

Revision ID: a5f6f06bb2c7
Revises: b99bff401293
Create Date: 2026-06-20 17:11:36.808734

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5f6f06bb2c7'
down_revision: Union[str, Sequence[str], None] = 'b99bff401293'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "check_actuator_time_values",
        "actuators",
        "activation_period >= 0 AND activation_duration >= 0"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("check_actuator_time_values", "actuators", type_="check")
