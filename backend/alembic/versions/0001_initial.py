"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-15 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("public_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("organization_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("venue", sa.String(length=255), nullable=False),
        sa.Column("contact_email", sa.String(length=254), nullable=True),
        sa.Column("contact_phone", sa.String(length=50), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("registration_open", sa.Boolean(), nullable=False),
        sa.Column("registration_start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("registration_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id"),
    )
    op.create_index(op.f("ix_events_id"), "events", ["id"], unique=False)

    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_admin_users_email"), "admin_users", ["email"], unique=False)
    op.create_index(op.f("ix_admin_users_id"), "admin_users", ["id"], unique=False)

    op.create_table(
        "registrations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("registration_id", sa.String(length=32), nullable=False),
        sa.Column("idempotency_key", sa.String(length=160), nullable=True),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("gender", sa.String(length=32), nullable=False),
        sa.Column("educational_qualification", sa.String(length=150), nullable=True),
        sa.Column("email", sa.String(length=254), nullable=True),
        sa.Column("normalised_email", sa.String(length=254), nullable=True),
        sa.Column("phone_number", sa.String(length=40), nullable=False),
        sa.Column("normalised_phone", sa.String(length=10), nullable=False),
        sa.Column("additional_contact_number", sa.String(length=40), nullable=True),
        sa.Column("normalised_additional_phone", sa.String(length=10), nullable=True),
        sa.Column("current_city", sa.String(length=120), nullable=False),
        sa.Column("alpha_alumni", sa.String(length=8), nullable=False),
        sa.Column("profession", sa.String(length=120), nullable=False),
        sa.Column("business_company_name", sa.String(length=150), nullable=False),
        sa.Column("attendance", sa.String(length=80), nullable=False),
        sa.Column("food_preference", sa.String(length=32), nullable=False),
        sa.Column("studied_standard", sa.String(length=80), nullable=True),
        sa.Column("year_of_passing", sa.String(length=20), nullable=True),
        sa.Column("professional_category", sa.String(length=120), nullable=False),
        sa.Column("industry", sa.String(length=150), nullable=False),
        sa.Column("consent_given", sa.Boolean(), nullable=False),
        sa.Column("registration_status", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("email_status", sa.String(length=16), nullable=False),
        sa.Column("email_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("email_failure_reason", sa.Text(), nullable=True),
        sa.Column("email_retry_count", sa.Integer(), nullable=False),
        sa.Column("google_sheet_sync_status", sa.String(length=16), nullable=False),
        sa.Column("google_sheet_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("google_sheet_failure_reason", sa.Text(), nullable=True),
        sa.Column("google_sheet_retry_count", sa.Integer(), nullable=False),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", "idempotency_key", name="uq_registration_event_idempotency_key"),
        sa.UniqueConstraint("event_id", "normalised_email", name="uq_registration_event_email"),
        sa.UniqueConstraint("event_id", "normalised_phone", name="uq_registration_event_phone"),
        sa.UniqueConstraint("registration_id"),
    )
    op.create_index(op.f("ix_registrations_email_status"), "registrations", ["email_status"], unique=False)
    op.create_index(op.f("ix_registrations_event_id"), "registrations", ["event_id"], unique=False)
    op.create_index(op.f("ix_registrations_google_sheet_sync_status"), "registrations", ["google_sheet_sync_status"], unique=False)
    op.create_index(op.f("ix_registrations_id"), "registrations", ["id"], unique=False)
    op.create_index(op.f("ix_registrations_registration_id"), "registrations", ["registration_id"], unique=False)
    op.create_index(op.f("ix_registrations_registration_status"), "registrations", ["registration_status"], unique=False)
    op.create_index(op.f("ix_registrations_source"), "registrations", ["source"], unique=False)
    op.create_index("ix_registrations_created_status", "registrations", ["created_at", "registration_status"], unique=False)
    op.create_index("ix_registrations_search_name", "registrations", ["full_name"], unique=False)

    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.String(length=80), nullable=False),
        sa.Column("old_values", sa.JSON(), nullable=True),
        sa.Column("new_values", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["admin_user_id"], ["admin_users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_audit_logs_action"), "admin_audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_admin_audit_logs_admin_user_id"), "admin_audit_logs", ["admin_user_id"], unique=False)
    op.create_index(op.f("ix_admin_audit_logs_created_at"), "admin_audit_logs", ["created_at"], unique=False)
    op.create_index(op.f("ix_admin_audit_logs_entity_id"), "admin_audit_logs", ["entity_id"], unique=False)
    op.create_index(op.f("ix_admin_audit_logs_entity_type"), "admin_audit_logs", ["entity_type"], unique=False)
    op.create_index(op.f("ix_admin_audit_logs_id"), "admin_audit_logs", ["id"], unique=False)


def downgrade() -> None:
    op.drop_table("admin_audit_logs")
    op.drop_table("registrations")
    op.drop_table("admin_users")
    op.drop_table("events")
