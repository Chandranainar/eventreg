export function eventDate(value: string): string {
  return new Intl.DateTimeFormat("en-IN", { day: "2-digit", month: "long", year: "numeric" }).format(new Date(value));
}

export function localDateTime(value: string): string {
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Asia/Kolkata"
  }).format(new Date(value));
}

export function eventTime(start: string, end: string): string {
  const format = (value: string) => {
    const [hour, minute] = value.split(":").map(Number);
    const date = new Date();
    date.setHours(hour, minute, 0, 0);
    return new Intl.DateTimeFormat("en-IN", { hour: "numeric", minute: "2-digit", hour12: true }).format(date);
  };
  return `${format(start)} to ${format(end)}`;
}

export function statusLabel(status: string): string {
  return status.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}
