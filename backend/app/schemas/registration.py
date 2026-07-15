from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

Gender = Literal["Male", "Female", "Other"]
YesNo = Literal["Yes", "No"]
Profession = Literal[
    "Entreprenuer & Startup Founder",
    "Doctors / Other Healthcare Professional",
    "Corporate Professional",
    "Educationalist",
    "Hospitality & Food Business",
    "Industrialist",
    "Retail Business Owner",
    "Media & Entertainment",
    "Civil & Infrastructure Professional",
    "Technology Company",
    "Finance & Consulting",
    "Legal & Governance",
    "Government & Public Service",
    "Agriculture & Sustainability",
]
Attendance = Literal["Will attend for sure", "Likely to attend", "Need to check on my schedule", "Not available"]
FoodPreference = Literal["Vegetarian", "Non-Vegetarian"]
RegistrationStatus = Literal["confirmed", "waitlisted", "cancelled", "attended", "no_show"]
EmailStatus = Literal["pending", "sent", "failed"]
SheetStatus = Literal["disabled", "pending", "synced", "failed"]
RegistrationSource = Literal["public_form", "admin_manual", "csv_import"]


class RegistrationCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone_number: str = Field(min_length=8, max_length=40)
    additional_contact_number: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None
    educational_qualification: str | None = Field(default=None, max_length=150)
    age: int = Field(ge=10, le=100)
    current_city: str = Field(min_length=2, max_length=120)
    gender: Gender
    profession: Profession
    business_company_name: str = Field(min_length=2, max_length=150)
    attendance: Attendance
    food_preference: FoodPreference
    alpha_alumni: YesNo
    studied_standard: str | None = Field(default=None, max_length=80)
    year_of_passing: str | None = Field(default=None, max_length=20)
    consent_given: bool = True

    @field_validator(
        "full_name",
        "phone_number",
        "additional_contact_number",
        "email",
        "educational_qualification",
        "current_city",
        "business_company_name",
        "studied_standard",
        "year_of_passing",
        mode="before",
    )
    @classmethod
    def trim_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("full_name", "current_city", "business_company_name")
    @classmethod
    def text_must_contain_letters(cls, value: str):
        if not any(char.isalpha() for char in value):
            raise ValueError("This field must contain letters.")
        return " ".join(value.split())

    @model_validator(mode="after")
    def require_alumni_details_when_needed(self):
        if self.alpha_alumni == "Yes" and (not self.studied_standard or not self.year_of_passing):
            raise ValueError("Alpha alumni school standard and passing year are required.")
        if not self.consent_given:
            raise ValueError("Consent is required.")
        return self


class ManualRegistrationCreate(RegistrationCreate):
    admin_notes: str | None = Field(default=None, max_length=5000)


class RegistrationPublicResult(BaseModel):
    registration_id: str
    full_name: str
    registration_status: RegistrationStatus
    email_status: EmailStatus
    google_sheet_sync_status: SheetStatus
    event_date: str
    event_time: str
    venue: str
    message: str


class RegistrationRead(BaseModel):
    id: int
    registration_id: str
    full_name: str
    phone_number: str
    additional_contact_number: str | None
    email: str | None
    educational_qualification: str | None
    age: int
    current_city: str
    gender: Gender
    profession: Profession
    business_company_name: str
    attendance: Attendance
    food_preference: FoodPreference
    alpha_alumni: YesNo
    studied_standard: str | None
    year_of_passing: str | None
    consent_given: bool
    registration_status: RegistrationStatus
    source: RegistrationSource
    email_status: EmailStatus
    email_sent_at: datetime | None
    email_failure_reason: str | None
    email_retry_count: int
    google_sheet_sync_status: SheetStatus
    google_sheet_synced_at: datetime | None
    google_sheet_failure_reason: str | None
    google_sheet_retry_count: int
    admin_notes: str | None
    created_at: datetime
    updated_at: datetime
    cancelled_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class RegistrationListItem(BaseModel):
    serial_number: int
    id: int
    created_at: datetime
    registration_id: str
    full_name: str
    phone_number: str
    additional_contact_number: str | None
    email: str | None
    educational_qualification: str | None
    age: int
    current_city: str
    gender: Gender
    profession: Profession
    business_company_name: str
    attendance: Attendance
    food_preference: FoodPreference
    alpha_alumni: YesNo
    studied_standard: str | None
    year_of_passing: str | None
    registration_status: RegistrationStatus
    email_status: EmailStatus
    google_sheet_sync_status: SheetStatus

    model_config = ConfigDict(from_attributes=True)


class PaginatedRegistrations(BaseModel):
    items: list[RegistrationListItem]
    total: int
    page: int
    page_size: int
    pages: int


class RegistrationUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=100)
    phone_number: str | None = Field(default=None, min_length=8, max_length=40)
    additional_contact_number: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None
    educational_qualification: str | None = Field(default=None, max_length=150)
    age: int | None = Field(default=None, ge=10, le=100)
    current_city: str | None = Field(default=None, min_length=2, max_length=120)
    gender: Gender | None = None
    profession: Profession | None = None
    business_company_name: str | None = Field(default=None, min_length=2, max_length=150)
    attendance: Attendance | None = None
    food_preference: FoodPreference | None = None
    alpha_alumni: YesNo | None = None
    studied_standard: str | None = Field(default=None, max_length=80)
    year_of_passing: str | None = Field(default=None, max_length=20)
    admin_notes: str | None = Field(default=None, max_length=5000)

    @field_validator(
        "full_name",
        "phone_number",
        "additional_contact_number",
        "email",
        "educational_qualification",
        "current_city",
        "business_company_name",
        "studied_standard",
        "year_of_passing",
        "admin_notes",
        mode="before",
    )
    @classmethod
    def trim_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class StatusUpdate(BaseModel):
    registration_status: RegistrationStatus
    admin_notes: str | None = Field(default=None, max_length=5000)


class ImportPreviewRequest(BaseModel):
    rows: list[dict[str, str]]
    mapping: dict[str, str]
    skip_duplicates: bool = True


class ImportPreviewRow(BaseModel):
    row_number: int
    valid: bool
    errors: list[str] = []
    duplicate: bool = False
    data: dict[str, str]


class ImportPreviewResponse(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicates: int
    rows: list[ImportPreviewRow]


class ImportConfirmResponse(BaseModel):
    total_rows: int
    successfully_imported: int
    duplicates_skipped: int
    invalid_rows: int
    failed_rows: int
