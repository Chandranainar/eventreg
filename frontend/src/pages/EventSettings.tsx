import { Save } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";

import { adminApi } from "../api/client";
import type { EventInfo } from "../types";

type EventForm = Partial<EventInfo>;

export default function EventSettings() {
  const [values, setValues] = useState<EventForm>({});
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    adminApi
      .event()
      .then((event) => setValues(event))
      .finally(() => setLoading(false));
  }, []);

  function update<K extends keyof EventForm>(key: K, value: EventForm[K]) {
    setValues((current) => ({ ...current, [key]: value }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = {
      name: values.name,
      organization_name: values.organization_name,
      description: values.description,
      event_date: values.event_date,
      start_time: values.start_time,
      end_time: values.end_time,
      venue: values.venue,
      contact_email: values.contact_email || null,
      contact_phone: values.contact_phone || null,
      capacity: values.capacity ? Number(values.capacity) : null,
      registration_open: values.registration_open,
      registration_start_at: values.registration_start_at || null,
      registration_end_at: values.registration_end_at || null
    };
    const updated = await adminApi.updateEvent(payload);
    setValues(updated);
    setMessage("Saved");
  }

  if (loading) return <section className="admin-section">Loading event settings...</section>;

  return (
    <section className="admin-section">
      <div className="admin-heading">
        <div>
          <span className="eyebrow">Configuration</span>
          <h1>Event settings</h1>
        </div>
      </div>
      {message && <div className="form-alert">{message}</div>}
      <form className="settings-form" onSubmit={submit}>
        <label>
          Event name
          <input value={values.name ?? ""} onChange={(event) => update("name", event.target.value)} required />
        </label>
        <label>
          Organization
          <input value={values.organization_name ?? ""} onChange={(event) => update("organization_name", event.target.value)} required />
        </label>
        <label className="span-2">
          Description
          <textarea value={values.description ?? ""} onChange={(event) => update("description", event.target.value)} rows={4} />
        </label>
        <label>
          Date
          <input type="date" value={values.event_date ?? ""} onChange={(event) => update("event_date", event.target.value)} required />
        </label>
        <label>
          Start time
          <input type="time" value={values.start_time?.slice(0, 5) ?? ""} onChange={(event) => update("start_time", event.target.value)} required />
        </label>
        <label>
          End time
          <input type="time" value={values.end_time?.slice(0, 5) ?? ""} onChange={(event) => update("end_time", event.target.value)} required />
        </label>
        <label>
          Maximum capacity
          <input type="number" min={1} value={values.capacity ?? ""} onChange={(event) => update("capacity", event.target.value ? Number(event.target.value) : null)} />
        </label>
        <label className="span-2">
          Venue
          <input value={values.venue ?? ""} onChange={(event) => update("venue", event.target.value)} required />
        </label>
        <label>
          Contact email
          <input type="email" value={values.contact_email ?? ""} onChange={(event) => update("contact_email", event.target.value)} />
        </label>
        <label>
          Contact phone
          <input value={values.contact_phone ?? ""} onChange={(event) => update("contact_phone", event.target.value)} />
        </label>
        <label>
          Registration opens
          <input type="datetime-local" value={toLocalInput(values.registration_start_at)} onChange={(event) => update("registration_start_at", fromLocalInput(event.target.value))} />
        </label>
        <label>
          Registration closes
          <input type="datetime-local" value={toLocalInput(values.registration_end_at)} onChange={(event) => update("registration_end_at", fromLocalInput(event.target.value))} />
        </label>
        <label className="toggle span-2">
          <input type="checkbox" checked={Boolean(values.registration_open)} onChange={(event) => update("registration_open", event.target.checked)} />
          Registration open
        </label>
        <button className="btn btn-primary" type="submit">
          <Save size={18} aria-hidden="true" />
          Save Settings
        </button>
      </form>
    </section>
  );
}

function toLocalInput(value?: string | null): string {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

function fromLocalInput(value: string): string | null {
  if (!value) return null;
  return new Date(value).toISOString();
}
