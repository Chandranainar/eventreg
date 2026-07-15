import { FileUp, Save } from "lucide-react";
import { ChangeEvent, useState } from "react";

import { adminApi } from "../api/client";

const fields = [
  "full_name",
  "phone_number",
  "additional_contact_number",
  "email",
  "educational_qualification",
  "age",
  "current_city",
  "gender",
  "profession",
  "business_company_name",
  "attendance",
  "food_preference",
  "alpha_alumni",
  "studied_standard",
  "year_of_passing",
  "consent_given"
];

const fieldAliases: Record<string, string> = {
  full_name: "full_name",
  official_contact_no: "phone_number",
  official_contact_number: "phone_number",
  contact_no: "phone_number",
  contact_number: "phone_number",
  phone_number: "phone_number",
  additional_contact_no: "additional_contact_number",
  additional_contact_number: "additional_contact_number",
  email_id: "email",
  email: "email",
  qualification: "educational_qualification",
  educational_qualification: "educational_qualification",
  age: "age",
  current_city_of_residence: "current_city",
  current_city: "current_city",
  gender: "gender",
  profession: "profession",
  business_company_name: "business_company_name",
  company_name: "business_company_name",
  attendance: "attendance",
  food_preference: "food_preference",
  alpha_school_alumni: "alpha_alumni",
  alpha_alumni: "alpha_alumni",
  studied_in_alpha_school_up_to_standard: "studied_standard",
  studied_standard: "studied_standard",
  year_of_passing_out_from_alpha_school: "year_of_passing",
  year_of_passing: "year_of_passing",
  consent_given: "consent_given"
};

function columnKey(column: string): string {
  return column.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
}

export default function AdminImport() {
  const [columns, setColumns] = useState<string[]>([]);
  const [rows, setRows] = useState<Record<string, string>[]>([]);
  const [mapping, setMapping] = useState<Record<string, string>>({});
  const [message, setMessage] = useState("");

  async function chooseFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    const preview = await adminApi.previewImport(file);
    setColumns(preview.columns);
    setRows(preview.rows ?? preview.sample_rows);
    const next: Record<string, string> = {};
    preview.columns.forEach((column) => {
      const target = fieldAliases[columnKey(column)];
      if (target && fields.includes(target)) next[column] = target;
    });
    setMapping(next);
    setMessage(`${preview.total_rows} rows loaded`);
  }

  async function confirm() {
    const response = await adminApi.confirmImport(rows, mapping, true);
    setMessage(JSON.stringify(response));
  }

  return (
    <section className="admin-section">
      <div className="admin-heading">
        <div>
          <span className="eyebrow">Migration</span>
          <h1>CSV import</h1>
        </div>
      </div>
      {message && <div className="form-alert">{message}</div>}
      <div className="import-panel">
        <label className="file-drop">
          <FileUp size={24} aria-hidden="true" />
          <span>Choose CSV</span>
          <input type="file" accept=".csv,text/csv" onChange={chooseFile} />
        </label>
        {columns.length > 0 && (
          <>
            <div className="mapping-grid">
              {columns.map((column) => (
                <label key={column}>
                  {column}
                  <select value={mapping[column] ?? ""} onChange={(event) => setMapping((current) => ({ ...current, [column]: event.target.value }))}>
                    <option value="">Ignore</option>
                    {fields.map((field) => (
                      <option key={field} value={field}>
                        {field}
                      </option>
                    ))}
                  </select>
                </label>
              ))}
            </div>
            <button className="btn btn-primary" type="button" onClick={confirm}>
              <Save size={18} aria-hidden="true" />
              Import Valid Rows
            </button>
          </>
        )}
      </div>
    </section>
  );
}
