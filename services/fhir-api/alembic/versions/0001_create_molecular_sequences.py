"""create molecular_sequences table

Revision ID: 0001
Revises:
Create Date: 2026-07-01

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "molecular_sequences",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("patient_reference", sa.String(), nullable=True),
        sa.Column("coordinate_system", sa.Integer(), nullable=False),
        sa.Column("resource", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_molecular_sequences_patient_reference",
        "molecular_sequences",
        ["patient_reference"],
    )


def downgrade() -> None:
    op.drop_index("ix_molecular_sequences_patient_reference", table_name="molecular_sequences")
    op.drop_table("molecular_sequences")
