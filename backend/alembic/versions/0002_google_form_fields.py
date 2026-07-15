"""add google form fields

Revision ID: 0002_google_form_fields
Revises: 0001_initial
Create Date: 2026-07-15 00:10:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_google_form_fields"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("registrations", sa.Column("additional_contact_number", sa.String(length=40), nullable=True))
    op.add_column("registrations", sa.Column("normalised_additional_phone", sa.String(length=10), nullable=True))
    op.add_column("registrations", sa.Column("current_city", sa.String(length=120), nullable=False, server_default="Chennai"))
    op.add_column("registrations", sa.Column("profession", sa.String(length=120), nullable=False, server_default="Technology Company"))
    op.add_column("registrations", sa.Column("business_company_name", sa.String(length=150), nullable=False, server_default="Not Provided"))
    op.add_column("registrations", sa.Column("attendance", sa.String(length=80), nullable=False, server_default="Will attend for sure"))
    op.add_column("registrations", sa.Column("food_preference", sa.String(length=32), nullable=False, server_default="Vegetarian"))
    op.add_column("registrations", sa.Column("studied_standard", sa.String(length=80), nullable=True))
    op.add_column("registrations", sa.Column("year_of_passing", sa.String(length=20), nullable=True))
    op.alter_column("registrations", "email", existing_type=sa.String(length=254), nullable=True)
    op.alter_column("registrations", "normalised_email", existing_type=sa.String(length=254), nullable=True)
    op.alter_column("registrations", "educational_qualification", existing_type=sa.String(length=150), nullable=True)


def downgrade() -> None:
    op.drop_column("registrations", "year_of_passing")
    op.drop_column("registrations", "studied_standard")
    op.drop_column("registrations", "food_preference")
    op.drop_column("registrations", "attendance")
    op.drop_column("registrations", "business_company_name")
    op.drop_column("registrations", "profession")
    op.drop_column("registrations", "current_city")
    op.drop_column("registrations", "normalised_additional_phone")
    op.drop_column("registrations", "additional_contact_number")
