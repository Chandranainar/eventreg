import { Link } from "react-router-dom";

import Logo from "../components/Logo";

export default function PrivacyNotice() {
  return (
    <main className="privacy-page">
      <Logo />
      <section className="privacy-panel">
        <h1>Privacy notice</h1>
        <p>
          Alpha Business Network collects registration details for event registration, event communication and attendance management.
          Access is limited to the event team. Details are not sold or published.
        </p>
        <p>For correction or assistance, contact the event team using the email or phone shown on the event page.</p>
        <Link className="btn btn-secondary" to="/">
          Back to Event
        </Link>
      </section>
    </main>
  );
}
