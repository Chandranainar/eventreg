export type EventInfo = {
  id?: number;
  public_id: string;
  name: string;
  organization_name: string;
  description?: string | null;
  event_date: string;
  start_time: string;
  end_time: string;
  venue: string;
  contact_email?: string | null;
  contact_phone?: string | null;
  capacity?: number | null;
  registration_open: boolean;
  registration_start_at?: string | null;
  registration_end_at?: string | null;
};

export type RegistrationPayload = {
  full_name: string;
  phone_number: string;
  additional_contact_number: string;
  email: string;
  educational_qualification: string;
  age: number | "";
  current_city: string;
  gender: string;
  profession: string;
  business_company_name: string;
  attendance: string;
  food_preference: string;
  alpha_alumni: string;
  studied_standard: string;
  year_of_passing: string;
  consent_given: boolean;
};

export type RegistrationResult = {
  registration_id: string;
  full_name: string;
  registration_status: "confirmed" | "waitlisted" | "cancelled" | "attended" | "no_show";
  email_status: "pending" | "sent" | "failed";
  google_sheet_sync_status: "disabled" | "pending" | "synced" | "failed";
  event_date: string;
  event_time: string;
  venue: string;
  message: string;
};

export type AdminUser = {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
  last_login_at?: string | null;
  csrf_token?: string | null;
};

export type DashboardSummary = {
  total_registrations: number;
  confirmed_registrations: number;
  waitlisted_registrations: number;
  cancelled_registrations: number;
  registrations_received_today: number;
  alpha_alumni_count: number;
  vegetarian_count: number;
  non_vegetarian_count: number;
  available_seats: number | null;
  failed_email_count: number;
  failed_google_sheets_sync_count: number;
};

export type RegistrationListItem = {
  serial_number: number;
  id: number;
  created_at: string;
  registration_id: string;
  full_name: string;
  phone_number: string;
  additional_contact_number?: string | null;
  email?: string | null;
  educational_qualification?: string | null;
  age: number;
  current_city: string;
  gender: string;
  profession: string;
  business_company_name: string;
  attendance: string;
  food_preference: string;
  alpha_alumni: string;
  studied_standard?: string | null;
  year_of_passing?: string | null;
  registration_status: string;
  email_status: string;
  google_sheet_sync_status: string;
};

export type RegistrationDetail = RegistrationListItem & {
  consent_given: boolean;
  source: string;
  email_sent_at?: string | null;
  email_failure_reason?: string | null;
  email_retry_count: number;
  google_sheet_synced_at?: string | null;
  google_sheet_failure_reason?: string | null;
  google_sheet_retry_count: number;
  admin_notes?: string | null;
  updated_at: string;
  cancelled_at?: string | null;
};

export type PaginatedRegistrations = {
  items: RegistrationListItem[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};
