import { Download, Filter, Search, SlidersHorizontal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { adminApi, exportUrl } from "../api/client";
import StatusBadge from "../components/StatusBadge";
import type { DashboardSummary, PaginatedRegistrations, RegistrationListItem } from "../types";
import { localDateTime } from "../utils/format";

const pageSizes = [25, 50, 100];
const professionOptions = [
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

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [records, setRecords] = useState<PaginatedRegistrations | null>(null);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState({
    registration_status: "",
    gender: "",
    alpha_alumni: "",
    profession: "",
    email_status: "",
    google_sheet_sync_status: "",
    sort: "newest",
    page_size: "25",
    page: "1"
  });
  const [loading, setLoading] = useState(true);

  const query = useMemo(() => {
    const params = new URLSearchParams();
    if (search.trim()) params.set("search", search.trim());
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    return params;
  }, [filters, search]);

  useEffect(() => {
    setLoading(true);
    Promise.all([adminApi.summary(), adminApi.registrations(query)])
      .then(([nextSummary, nextRecords]) => {
        setSummary(nextSummary);
        setRecords(nextRecords);
      })
      .finally(() => setLoading(false));
  }, [query]);

  function setFilter(key: keyof typeof filters, value: string) {
    setFilters((current) => ({ ...current, [key]: value, page: key === "page" ? value : "1" }));
  }

  return (
    <section className="admin-section">
      <div className="admin-heading">
        <div>
          <span className="eyebrow">Responses</span>
          <h1>Registration dashboard</h1>
        </div>
        <div className="export-actions">
          <a className="btn btn-secondary" href={exportUrl("csv", query)}>
            <Download size={18} aria-hidden="true" />
            CSV
          </a>
          <a className="btn btn-secondary" href={exportUrl("xlsx", query)}>
            <Download size={18} aria-hidden="true" />
            XLSX
          </a>
        </div>
      </div>

      {summary && (
        <div className="dashboard-summary">
          <div className="overview-panel">
            <div className="overview-main">
              <Metric label="Total responses" value={summary.total_registrations} />
              <Metric label="Confirmed" value={summary.confirmed_registrations} />
              <Metric label="Seats left" value={summary.available_seats ?? "Open"} />
              <Metric label="Today" value={summary.registrations_received_today} />
            </div>
            <details className="summary-breakdown">
              <summary>
                <SlidersHorizontal size={18} aria-hidden="true" />
                View breakdown
              </summary>
              <div className="breakdown-list">
                <BreakdownItem label="Waitlisted" value={summary.waitlisted_registrations} />
                <BreakdownItem label="Cancelled" value={summary.cancelled_registrations} />
                <BreakdownItem label="Alumni" value={summary.alpha_alumni_count} />
                <BreakdownItem label="Vegetarian" value={summary.vegetarian_count} />
                <BreakdownItem label="Non-veg" value={summary.non_vegetarian_count} />
                <BreakdownItem label="Email failed" value={summary.failed_email_count} tone={summary.failed_email_count ? "warn" : ""} />
                <BreakdownItem label="Sheet failed" value={summary.failed_google_sheets_sync_count} tone={summary.failed_google_sheets_sync_count ? "warn" : ""} />
              </div>
            </details>
          </div>
        </div>
      )}

      <div className="table-tools">
        <div className="toolbar-primary">
          <label className="search-box">
            <Search size={18} aria-hidden="true" />
            <input placeholder="Search name, ID, email, phone, city, profession or company" value={search} onChange={(event) => setSearch(event.target.value)} />
          </label>
          <div className="quick-filters">
            <Select label="Status" value={filters.registration_status} onChange={(value) => setFilter("registration_status", value)} options={["confirmed", "waitlisted", "cancelled", "attended", "no_show"]} />
            <Select label="Sort" value={filters.sort} onChange={(value) => setFilter("sort", value)} options={["newest", "oldest", "name", "registration_id", "status"]} />
          </div>
        </div>
        <details className="filter-drawer">
          <summary>
            <SlidersHorizontal size={18} aria-hidden="true" />
            More filters
          </summary>
          <div className="filter-grid">
            <Select label="Gender" value={filters.gender} onChange={(value) => setFilter("gender", value)} options={["Male", "Female", "Other"]} />
            <Select label="Alumni" value={filters.alpha_alumni} onChange={(value) => setFilter("alpha_alumni", value)} options={["Yes", "No"]} />
            <Select label="Profession" value={filters.profession} onChange={(value) => setFilter("profession", value)} options={professionOptions} />
            <Select label="Email" value={filters.email_status} onChange={(value) => setFilter("email_status", value)} options={["pending", "sent", "failed"]} />
            <Select label="Sheet" value={filters.google_sheet_sync_status} onChange={(value) => setFilter("google_sheet_sync_status", value)} options={["disabled", "pending", "synced", "failed"]} />
          </div>
        </details>
      </div>

      <div className="table-frame" aria-busy={loading}>
        <div className="table-title">
          <span>
            <Filter size={18} aria-hidden="true" />
            {records ? `${records.total} responses` : "Responses"}
          </span>
          <select value={filters.page_size} onChange={(event) => setFilter("page_size", event.target.value)}>
            {pageSizes.map((size) => (
              <option key={size} value={size}>
                {size} per page
              </option>
            ))}
          </select>
        </div>
        <table className="responses-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Submitted</th>
              <th>Registration ID</th>
              <th>Full name</th>
              <th>Official contact</th>
              <th>Additional contact</th>
              <th>Email</th>
              <th>Qualification</th>
              <th>Age</th>
              <th>City</th>
              <th>Gender</th>
              <th>Profession</th>
              <th>Business / Company</th>
              <th>Attendance</th>
              <th>Food</th>
              <th>Alumni</th>
              <th>Standard</th>
              <th>Passing year</th>
              <th>Status</th>
              <th>Email status</th>
              <th>Sheet status</th>
            </tr>
          </thead>
          <tbody>
            {records?.items.map((item) => (
              <tr key={item.registration_id} onClick={() => navigate(`/admin/registrations/${item.registration_id}`)} tabIndex={0}>
                <td>{item.serial_number}</td>
                <td>{localDateTime(item.created_at)}</td>
                <td>{item.registration_id}</td>
                <td>{item.full_name}</td>
                <td>{item.phone_number}</td>
                <td>{display(item.additional_contact_number)}</td>
                <td>{display(item.email)}</td>
                <td>{display(item.educational_qualification)}</td>
                <td>{item.age}</td>
                <td>{item.current_city}</td>
                <td>{item.gender}</td>
                <td>{item.profession}</td>
                <td>{item.business_company_name}</td>
                <td>{item.attendance}</td>
                <td>{item.food_preference}</td>
                <td>{item.alpha_alumni}</td>
                <td>{display(item.studied_standard)}</td>
                <td>{display(item.year_of_passing)}</td>
                <td><StatusBadge value={item.registration_status} /></td>
                <td><StatusBadge value={item.email_status} /></td>
                <td><StatusBadge value={item.google_sheet_sync_status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="response-cards">
          {records?.items.map((item) => (
            <button className="response-card" key={item.registration_id} type="button" onClick={() => navigate(`/admin/registrations/${item.registration_id}`)}>
              <ResponseCard item={item} />
            </button>
          ))}
        </div>
        {records && (
          <div className="pagination">
            <button className="btn btn-secondary" type="button" disabled={records.page <= 1} onClick={() => setFilter("page", String(records.page - 1))}>
              Previous
            </button>
            <span>
              Page {records.page} of {records.pages}
            </span>
            <button className="btn btn-secondary" type="button" disabled={records.page >= records.pages} onClick={() => setFilter("page", String(records.page + 1))}>
              Next
            </button>
          </div>
        )}
      </div>
    </section>
  );
}

function Metric({ label, value, tone = "" }: { label: string; value: number | string; tone?: string }) {
  return (
    <article className={`metric ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function BreakdownItem({ label, value, tone = "" }: { label: string; value: number | string; tone?: string }) {
  return (
    <div className={`breakdown-item ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Select({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (value: string) => void }) {
  return (
    <label>
      {label}
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">All</option>
        {options.map((option) => (
          <option key={option} value={option}>
            {option.replace(/_/g, " ")}
          </option>
        ))}
      </select>
    </label>
  );
}

function ResponseCard({ item }: { item: RegistrationListItem }) {
  return (
    <>
      <span>{item.serial_number}</span>
      <strong>{item.full_name}</strong>
      <small>{item.registration_id} · {localDateTime(item.created_at)}</small>
      <div>
        <StatusBadge value={item.registration_status} />
        <StatusBadge value={item.email_status} />
      </div>
      <p>{display(item.email)} · {item.phone_number}</p>
    </>
  );
}

function display(value?: string | null): string {
  return value?.trim() ? value : "-";
}
