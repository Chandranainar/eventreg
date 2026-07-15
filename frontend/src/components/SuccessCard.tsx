import { CheckCircle2, RotateCcw } from "lucide-react";

import type { RegistrationResult } from "../types";
import { statusLabel } from "../utils/format";

type SuccessCardProps = {
  result: RegistrationResult;
  onReset: () => void;
};

export default function SuccessCard({ result, onReset }: SuccessCardProps) {
  return (
    <section className="success-card" aria-live="polite">
      <CheckCircle2 size={44} strokeWidth={1.8} aria-hidden="true" />
      <h2>{statusLabel(result.registration_status)}</h2>
      <p>{result.message}</p>
      <dl className="success-details">
        <div>
          <dt>Name</dt>
          <dd>{result.full_name}</dd>
        </div>
        <div>
          <dt>Registration ID</dt>
          <dd>{result.registration_id}</dd>
        </div>
        <div>
          <dt>Date</dt>
          <dd>{result.event_date}</dd>
        </div>
        <div>
          <dt>Time</dt>
          <dd>{result.event_time}</dd>
        </div>
        <div>
          <dt>Venue</dt>
          <dd>{result.venue}</dd>
        </div>
        <div>
          <dt>Email status</dt>
          <dd>{statusLabel(result.email_status)}</dd>
        </div>
      </dl>
      <button className="btn btn-secondary" type="button" onClick={onReset}>
        <RotateCcw size={18} aria-hidden="true" />
        Register Another Attendee
      </button>
    </section>
  );
}
