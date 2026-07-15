import { AlertCircle, Send } from "lucide-react";
import type { FormEvent, ReactNode } from "react";
import { useMemo, useState } from "react";

import { ApiError, publicApi } from "../api/client";
import type { EventInfo, RegistrationPayload, RegistrationResult } from "../types";
import { newIdempotencyKey, validateRegistration } from "../utils/validation";
import SuccessCard from "./SuccessCard";

const professions = [
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
  "Agriculture & Sustainability"
];

const initialValues: RegistrationPayload = {
  full_name: "",
  phone_number: "",
  additional_contact_number: "",
  email: "",
  educational_qualification: "",
  age: "",
  current_city: "",
  gender: "",
  profession: "",
  business_company_name: "",
  attendance: "",
  food_preference: "",
  alpha_alumni: "",
  studied_standard: "",
  year_of_passing: "",
  consent_given: true
};

type RegistrationFormProps = {
  event: EventInfo;
};

export default function RegistrationForm({ event }: RegistrationFormProps) {
  const [values, setValues] = useState<RegistrationPayload>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<RegistrationResult | null>(null);
  const [submitError, setSubmitError] = useState("");
  const [idempotencyKey, setIdempotencyKey] = useState(() => newIdempotencyKey());
  const closed = !event.registration_open;
  const fieldId = useMemo(() => `registration-${event.public_id}`, [event.public_id]);

  function update<K extends keyof RegistrationPayload>(key: K, value: RegistrationPayload[K]) {
    setValues((current) => ({ ...current, [key]: value }));
    setErrors((current) => ({ ...current, [key]: "" }));
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitError("");
    const nextErrors = validateRegistration(values);
    setErrors(nextErrors);
    if (Object.values(nextErrors).some(Boolean)) return;
    setSubmitting(true);
    try {
      const response = await publicApi.register(values, idempotencyKey);
      setResult(response);
    } catch (error) {
      if (error instanceof ApiError && error.code === "DUPLICATE_REGISTRATION") {
        setSubmitError("A registration already exists with this official contact number or email address.");
      } else if (error instanceof ApiError && error.code === "REGISTRATION_CLOSED") {
        setSubmitError("Registration for this event is currently closed.");
      } else if (error instanceof ApiError) {
        setSubmitError(error.message);
      } else {
        setSubmitError("Unable to submit registration. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  function reset() {
    setValues(initialValues);
    setErrors({});
    setResult(null);
    setSubmitError("");
    setIdempotencyKey(newIdempotencyKey());
    document.getElementById("register")?.scrollIntoView({ behavior: "smooth" });
  }

  if (result) return <SuccessCard result={result} onReset={reset} />;

  return (
    <form className="registration-form" onSubmit={onSubmit} noValidate>
      {closed && <div className="form-alert">Registration for this event is currently closed.</div>}
      {submitError && (
        <div className="form-alert error" role="alert">
          <AlertCircle size={18} aria-hidden="true" />
          {submitError}
        </div>
      )}
      <div className="form-grid">
        <Field label="Full Name" inputId={`${fieldId}-full-name`} required error={errors.full_name}>
          <input id={`${fieldId}-full-name`} value={values.full_name} onChange={(event) => update("full_name", event.target.value)} disabled={closed || submitting} />
        </Field>
        <Field label="Official Contact No" inputId={`${fieldId}-phone`} required error={errors.phone_number}>
          <input id={`${fieldId}-phone`} inputMode="tel" value={values.phone_number} onChange={(event) => update("phone_number", event.target.value)} disabled={closed || submitting} />
        </Field>
        <Field label="Additional Contact No" inputId={`${fieldId}-additional-phone`} error={errors.additional_contact_number}>
          <input id={`${fieldId}-additional-phone`} inputMode="tel" value={values.additional_contact_number} onChange={(event) => update("additional_contact_number", event.target.value)} disabled={closed || submitting} />
        </Field>
        <Field label="Email Id" inputId={`${fieldId}-email`} error={errors.email}>
          <input id={`${fieldId}-email`} type="email" value={values.email} onChange={(event) => update("email", event.target.value)} disabled={closed || submitting} />
        </Field>
        <Field label="Qualification" inputId={`${fieldId}-qualification`} error={errors.educational_qualification}>
          <input id={`${fieldId}-qualification`} value={values.educational_qualification} onChange={(event) => update("educational_qualification", event.target.value)} disabled={closed || submitting} />
        </Field>
        <Field label="Age" inputId={`${fieldId}-age`} required error={errors.age}>
          <input id={`${fieldId}-age`} type="number" min={10} max={100} value={values.age} onChange={(event) => update("age", event.target.value === "" ? "" : Number(event.target.value))} disabled={closed || submitting} />
        </Field>
        <Field label="Current City of Residence" inputId={`${fieldId}-city`} required error={errors.current_city}>
          <input id={`${fieldId}-city`} value={values.current_city} onChange={(event) => update("current_city", event.target.value)} disabled={closed || submitting} />
        </Field>
        <Field label="Gender" inputId={`${fieldId}-gender`} required error={errors.gender}>
          <select id={`${fieldId}-gender`} value={values.gender} onChange={(event) => update("gender", event.target.value)} disabled={closed || submitting}>
            <option value="">Select</option>
            <option>Male</option>
            <option>Female</option>
            <option>Other</option>
          </select>
        </Field>
        <Field label="Profession" inputId={`${fieldId}-profession`} required error={errors.profession}>
          <select id={`${fieldId}-profession`} value={values.profession} onChange={(event) => update("profession", event.target.value)} disabled={closed || submitting}>
            <option value="">Select</option>
            {professions.map((profession) => (
              <option key={profession}>{profession}</option>
            ))}
          </select>
        </Field>
        <Field label="Business / Company Name" inputId={`${fieldId}-company`} required error={errors.business_company_name}>
          <input id={`${fieldId}-company`} value={values.business_company_name} onChange={(event) => update("business_company_name", event.target.value)} disabled={closed || submitting} />
        </Field>
        <ChoiceField label="Attendance" required error={errors.attendance}>
          {["Will attend for sure", "Likely to attend", "Need to check on my schedule", "Not available"].map((option) => (
            <Choice key={option} name="attendance" value={option} checked={values.attendance === option} onChange={() => update("attendance", option)} disabled={closed || submitting} />
          ))}
        </ChoiceField>
        <ChoiceField label="Food Preference" required error={errors.food_preference}>
          {["Vegetarian", "Non-Vegetarian"].map((option) => (
            <Choice key={option} name="food_preference" value={option} checked={values.food_preference === option} onChange={() => update("food_preference", option)} disabled={closed || submitting} />
          ))}
        </ChoiceField>
        <ChoiceField label="Alpha School Alumni" required error={errors.alpha_alumni}>
          {["Yes", "No"].map((option) => (
            <Choice key={option} name="alpha_alumni" value={option} checked={values.alpha_alumni === option} onChange={() => update("alpha_alumni", option)} disabled={closed || submitting} />
          ))}
        </ChoiceField>
        {values.alpha_alumni === "Yes" && (
          <>
            <Field label="Studied in Alpha School up to? (Standard)" inputId={`${fieldId}-standard`} required error={errors.studied_standard}>
              <input id={`${fieldId}-standard`} value={values.studied_standard} onChange={(event) => update("studied_standard", event.target.value)} disabled={closed || submitting} />
            </Field>
            <Field label="Year of passing out from Alpha School" inputId={`${fieldId}-year`} required error={errors.year_of_passing}>
              <input id={`${fieldId}-year`} inputMode="numeric" value={values.year_of_passing} onChange={(event) => update("year_of_passing", event.target.value)} disabled={closed || submitting} />
            </Field>
          </>
        )}
      </div>
      <p className="consent-note">By submitting, you agree that Alpha Business Network may use these details for event registration, communication and attendance management.</p>
      <button className="btn btn-primary submit-btn" type="submit" disabled={closed || submitting}>
        <Send size={18} aria-hidden="true" />
        {submitting ? "Submitting..." : "Submit Registration"}
      </button>
    </form>
  );
}

function Field({ label, inputId, required, error, children }: { label: string; inputId: string; required?: boolean; error?: string; children: ReactNode }) {
  return (
    <div className="field">
      <label htmlFor={inputId}>
        {label}
        {required && <span aria-hidden="true"> *</span>}
      </label>
      {children}
      {error && <p className="field-error">{error}</p>}
    </div>
  );
}

function ChoiceField({ label, required, error, children }: { label: string; required?: boolean; error?: string; children: ReactNode }) {
  return (
    <fieldset className="choice-field">
      <legend>
        {label}
        {required && <span aria-hidden="true"> *</span>}
      </legend>
      <div className="choice-pills">{children}</div>
      {error && <p className="field-error">{error}</p>}
    </fieldset>
  );
}

function Choice({ name, value, checked, onChange, disabled }: { name: string; value: string; checked: boolean; onChange: () => void; disabled: boolean }) {
  return (
    <label className="choice-pill">
      <input type="radio" name={name} value={value} checked={checked} onChange={onChange} disabled={disabled} />
      <span>{value}</span>
    </label>
  );
}
