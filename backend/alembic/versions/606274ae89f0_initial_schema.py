"""initial schema

Revision ID: 606274ae89f0
Revises: 
Create Date: 2026-11-09 13:36:01.343459

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '606274ae89f0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('prototypes',
    sa.Column('prototype_id', sa.Integer(), nullable=False),
    sa.Column('prototype_name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('prototype_id')
    )
    op.create_table('users',
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('pw_salt', sa.String(), nullable=False),
    sa.Column('pw_hash', sa.String(), nullable=False),
    sa.Column('permissions', sa.Integer(), nullable=False),
    sa.Column('logged_in', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('username'),
    )
    op.create_table('sensors',
    sa.Column('sensor_id', sa.Integer(), nullable=False),
    sa.Column('sensor_type', sa.Enum('temperature', 'humidity', 'ec', 'ph', 'water_level', 'boolean_water_level', 'oxygen', name='sensortype'), nullable=False),
    sa.Column('prototype_id', sa.Integer(), nullable=False),
    sa.Column('threshold_critically_low', sa.Float(), nullable=False),
    sa.Column('threshold_low', sa.Float(), nullable=False),
    sa.Column('threshold_high', sa.Float(), nullable=False),
    sa.Column('threshold_critically_high', sa.Float(), nullable=False),
    sa.Column('sensor_unit', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['prototype_id'], ['prototypes.prototype_id'], ),
    sa.PrimaryKeyConstraint('sensor_id')
    )
    op.create_table('actuators',
    sa.Column('actuator_id', sa.Integer(), nullable=False),
    sa.Column('actuator_type', sa.Enum('acid_pump', 'base_pump', 'nutrients_A_pump', 'nutrients_B_pump', name='actuatortype'), nullable=False),
    sa.Column('sensor_id', sa.Integer(), nullable=False),
    sa.Column('condition_value', sa.Float(), nullable=False),
    sa.Column('activation_condition', sa.Enum('high', 'low', 'low_or_high', 'always', name='activationcondition'), nullable=False),
    sa.Column('activation_period', sa.Float(), nullable=False),
    sa.Column('activation_duration', sa.Float(), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('last_activated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['sensor_id'], ['sensors.sensor_id'], ),
    sa.PrimaryKeyConstraint('actuator_id')
    )
    op.create_table('measurements',
    sa.Column('measurement_id', sa.Integer(), nullable=False),
    sa.Column('sensor_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['sensor_id'], ['sensors.sensor_id'], ),
    sa.PrimaryKeyConstraint('measurement_id')
    )
    op.create_index(op.f('ix_measurements_sensor_id'), 'measurements', ['sensor_id'], unique=False)
    op.create_index(op.f('ix_measurements_timestamp'), 'measurements', ['timestamp'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_measurements_timestamp'), table_name='measurements')
    op.drop_index(op.f('ix_measurements_sensor_id'), table_name='measurements')
    op.drop_table('measurements')
    op.drop_table('actuators')
    op.drop_table('sensors')
    op.drop_table('users')
    op.drop_table('prototypes')
    op.execute("DROP TYPE activationcondition")
    op.execute("DROP TYPE actuatortype")
    op.execute("DROP TYPE sensortype")
