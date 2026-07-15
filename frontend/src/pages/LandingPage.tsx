import { CalendarDays, Clock, Mail, MapPin, Phone, Users } from "lucide-react";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";

import { publicApi } from "../api/client";
import eventBrandBanner from "../assets/event-brand-banner-premium.png";
import Logo from "../components/Logo";
import RegistrationForm from "../components/RegistrationForm";
import type { EventInfo } from "../types";
import { eventDate, eventTime } from "../utils/format";

export default function LandingPage() {
  const [event, setEvent] = useState<EventInfo | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    publicApi
      .event()
      .then(setEvent)
      .catch(() => setError("Event details are unavailable right now."));
  }, []);

  function scrollToRegistration() {
    document.getElementById("register")?.scrollIntoView({ behavior: "smooth" });
  }

  if (error) {
    return (
      <main className="center-state">
        <Logo />
        <p>{error}</p>
      </main>
    );
  }

  if (!event) {
    return (
      <main className="center-state">
        <Logo />
        <p>Loading event details...</p>
      </main>
    );
  }

  return (
    <div className="site-shell">
      <header className="public-header">
        <Logo />
        <nav aria-label="Primary navigation">
          <a href="#register">Registration</a>
          <button className="btn btn-primary" type="button" onClick={scrollToRegistration}>
            <Users size={18} aria-hidden="true" />
            Register
          </button>
        </nav>
      </header>

      <section className="hero">
        <div className="hero-layer glow" aria-hidden="true" />
        <div className="hero-layer motes" aria-hidden="true">
          {Array.from({ length: 10 }).map((_, index) => <span key={index} />)}
        </div>
        <div className="hero-content">
          <figure className="event-brand-banner">
            <img src={eventBrandBanner} alt="ABN and Alpha Group of Institutions - Entrepreneurs and Professionals Meet" />
          </figure>
          <h1 className="sr-only">Entrepreneurs & Professionals Meet</h1>
          <p>{event.description}</p>
          <div className="gold-rule"><span /></div>
          <div className="hero-meta" aria-label="Event details">
            <span>
              <CalendarDays size={18} aria-hidden="true" />
              {eventDate(event.event_date)}
            </span>
            <span>
              <Clock size={18} aria-hidden="true" />
              {eventTime(event.start_time, event.end_time)}
            </span>
            <span>
              <MapPin size={18} aria-hidden="true" />
              {event.venue}
            </span>
          </div>
          <button className="btn btn-primary hero-btn" type="button" onClick={scrollToRegistration}>
            <Users size={18} aria-hidden="true" />
            Register Now
          </button>
        </div>
      </section>

      <main>
        <section className="info-band" aria-label="Event information">
          <InfoCard icon={<CalendarDays size={22} />} title="Date" value={eventDate(event.event_date)} />
          <InfoCard icon={<Clock size={22} />} title="Time" value={eventTime(event.start_time, event.end_time)} />
          <InfoCard icon={<MapPin size={22} />} title="Venue" value={event.venue} />
        </section>

        <section id="register" className="registration-section">
          <div className="section-heading">
            <span className="eyebrow">Registration</span>
            <h2>Event Registration</h2>
          </div>
          <RegistrationForm event={event} />
        </section>
      </main>

      <footer className="public-footer">
        <Logo compact />
        <div>
          <strong>{event.organization_name}</strong>
          <span>{eventDate(event.event_date)} · {event.venue}</span>
        </div>
        <div className="footer-contact">
          {event.contact_email && (
            <span>
              <Mail size={16} aria-hidden="true" />
              {event.contact_email}
            </span>
          )}
          {event.contact_phone && (
            <span>
              <Phone size={16} aria-hidden="true" />
              {event.contact_phone}
            </span>
          )}
          <a href="/privacy">Privacy notice</a>
        </div>
      </footer>
    </div>
  );
}

function InfoCard({ icon, title, value }: { icon: ReactNode; title: string; value: string }) {
  return (
    <article className="info-card">
      <span aria-hidden="true">{icon}</span>
      <div>
        <h3>{title}</h3>
        <p>{value}</p>
      </div>
    </article>
  );
}
