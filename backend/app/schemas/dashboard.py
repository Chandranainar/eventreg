from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_registrations: int
    confirmed_registrations: int
    waitlisted_registrations: int
    cancelled_registrations: int
    registrations_received_today: int
    alpha_alumni_count: int
    vegetarian_count: int
    non_vegetarian_count: int
    available_seats: int | None
    failed_email_count: int
    failed_google_sheets_sync_count: int


class RegistrationTrend(BaseModel):
    date: str
    count: int
