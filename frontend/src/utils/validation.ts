import type { RegistrationPayload } from "../types";

export type FormErrors = Partial<Record<keyof RegistrationPayload, string>>;

function validIndianPhone(value: string, required: boolean): boolean {
  if (!value.trim()) return !required;
  const digits = value.replace(/\D/g, "");
  const phone = digits.startsWith("91") && digits.length === 12 ? digits.slice(2) : digits.startsWith("0") && digits.length === 11 ? digits.slice(1) : digits;
  return /^[6-9]\d{9}$/.test(phone);
}

function hasLetters(value: string): boolean {
  return /[a-z]/i.test(value.trim());
}

export function validateRegistration(values: RegistrationPayload): FormErrors {
  const errors: FormErrors = {};
  if (!values.full_name.trim() || values.full_name.trim().length < 2 || !hasLetters(values.full_name)) {
    errors.full_name = "Enter the full name.";
  }
  if (!validIndianPhone(values.phone_number, true)) {
    errors.phone_number = "Enter a valid official Indian mobile number.";
  }
  if (!validIndianPhone(values.additional_contact_number, false)) {
    errors.additional_contact_number = "Enter a valid additional Indian mobile number.";
  }
  if (values.email.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email.trim())) {
    errors.email = "Enter a valid email address.";
  }
  if (values.age === "" || Number(values.age) < 10 || Number(values.age) > 100) {
    errors.age = "Age must be between 10 and 100.";
  }
  if (!values.current_city.trim() || !hasLetters(values.current_city)) {
    errors.current_city = "Enter current city of residence.";
  }
  if (!values.gender) errors.gender = "Select gender.";
  if (!values.profession) errors.profession = "Select profession.";
  if (!values.business_company_name.trim() || !hasLetters(values.business_company_name)) {
    errors.business_company_name = "Enter business or company name.";
  }
  if (!values.attendance) errors.attendance = "Select attendance.";
  if (!values.food_preference) errors.food_preference = "Select food preference.";
  if (!values.alpha_alumni) errors.alpha_alumni = "Select alumni status.";
  if (values.alpha_alumni === "Yes") {
    if (!values.studied_standard.trim()) errors.studied_standard = "Enter studied standard.";
    if (!values.year_of_passing.trim()) errors.year_of_passing = "Enter year of passing.";
  }
  return errors;
}

export function newIdempotencyKey(): string {
  return crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}
