"""image models

Revision ID: d65f30c26e45
Revises: 1687506a0bf8
Create Date: 2024-09-14 20:58:00.740826

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d65f30c26e45"
down_revision = "1687506a0bf8"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "image_data_files",
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("path", sa.String(length=255), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("image_data_files")
    # ### end Alembic commands ###
