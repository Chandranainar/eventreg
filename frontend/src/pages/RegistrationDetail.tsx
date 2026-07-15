import { ArrowLeft, RefreshCw, Save } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { adminApi } from "../api/client";
import StatusBadge from "../components/StatusBadge";
import type { RegistrationDetail as Detail } from "../types";
import { localDateTime, statusLabel } from "../utils/format";

export default function RegistrationDetail() {
  const { id = "" } = useParams();
  const [detail, setDetail] = useState<Detail | null>(null);
  const [status, setStatus] = useState("confirmed");
  const [notes, setNotes] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    adminApi.registration(id).then((record) => {
      setDetail(record);
      setStatus(record.registration_status);
      setNotes(record.admin_notes ?? "");
    });
  }, [id]);

  async function saveStatus(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const updated = await adminApi.updateStatus(id, status, notes);
    setDetail(updated);
    setMessage("Saved");
  }

  async function retry(kind: "email" | "sheet") {
    const updated = kind === "email" ? await adminApi.retryEmail(id) : await adminApi.retrySheet(id);
    setDetail(updated);
    setMessage(kind === "email" ? "Email retry completed" : "Sheet sync retry completed");
  }

  if (!detail) return <section className="admin-section">Loading registration...</section>;

  return (
    <section className="admin-section">
      <div className="admin-heading">
        <div>
          <Link className="back-link" to="/admin">
            <ArrowLeft size={18} aria-hidden="true" />
            Back
          </Link>
          <h1>{detail.full_name}</h1>
          <p>{detail.registration_id}</p>
        </div>
        <StatusBadge value={detail.registration_status} />
      </div>
      {message && <div className="form-alert">{message}</div>}

      <div className="detail-grid">
        <section className="detail-panel">
          <h2>Registration</h2>
          <dl>
            <Row label="Submitted" value={localDateTime(detail.created_at)} />
            <Row label="Updated" value={localDateTime(detail.updated_at)} />
            <Row label="Official contact" value={detail.phone_number} />
            <Row label="Additional contact" value={detail.additional_contact_number} />
            <Row label="Email" value={detail.email} />
            <Row label="Qualification" value={detail.educational_qualification} />
            <Row label="Age" value={detail.age} />
            <Row label="Current city" value={detail.current_city} />
            <Row label="Gender" value={detail.gender} />
            <Row label="Profession" value={detail.profession} />
            <Row label="Business / Company" value={detail.business_company_name} />
            <Row label="Attendance" value={detail.attendance} />
            <Row label="Food preference" value={detail.food_preference} />
            <Row label="Alpha alumni" value={detail.alpha_alumni} />
            <Row label="Studied up to" value={detail.studied_standard} />
            <Row label="Passing year" value={detail.year_of_passing} />
            <Row label="Source" value={statusLabel(detail.source)} />
          </dl>
        </section>

        <section className="detail-panel">
          <h2>Delivery</h2>
          <dl>
            <Row label="Email status" value={statusLabel(detail.email_status)} />
            <Row label="Email sent" value={detail.email_sent_at ? localDateTime(detail.email_sent_at) : "Not sent"} />
            <Row label="Email retries" value={detail.email_retry_count} />
            <Row label="Email failure" value={detail.email_failure_reason ?? "None"} />
            <Row label="Sheet status" value={statusLabel(detail.google_sheet_sync_status)} />
            <Row label="Sheet synced" value={detail.google_sheet_synced_at ? localDateTime(detail.google_sheet_synced_at) : "Not synced"} />
            <Row label="Sheet retries" value={detail.google_sheet_retry_count} />
            <Row label="Sheet failure" value={detail.google_sheet_failure_reason ?? "None"} />
          </dl>
          <div className="button-row">
            <button className="btn btn-secondary" type="button" onClick={() => retry("email")}>
              <RefreshCw size={18} aria-hidden="true" />
              Retry Email
            </button>
            <button className="btn btn-secondary" type="button" onClick={() => retry("sheet")}>
              <RefreshCw size={18} aria-hidden="true" />
              Retry Sheet
            </button>
          </div>
        </section>

        <form className="detail-panel" onSubmit={saveStatus}>
          <h2>Admin action</h2>
          <label>
            Status
            <select value={status} onChange={(event) => setStatus(event.target.value)}>
              <option value="confirmed">Confirmed</option>
              <option value="waitlisted">Waitlisted</option>
              <option value="cancelled">Cancelled</option>
              <option value="attended">Attended</option>
              <option value="no_show">No show</option>
            </select>
          </label>
          <label>
            Admin notes
            <textarea value={notes} onChange={(event) => setNotes(event.target.value)} rows={6} />
          </label>
          <button className="btn btn-primary" type="submit">
            <Save size={18} aria-hidden="true" />
            Save
          </button>
        </form>
      </div>
    </section>
  );
}

function Row({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value === null || value === undefined || value === "" ? "-" : value}</dd>
    </div>
  );
}
