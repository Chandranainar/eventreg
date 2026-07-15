import { statusLabel } from "../utils/format";

type StatusBadgeProps = {
  value: string;
};

export default function StatusBadge({ value }: StatusBadgeProps) {
  return <span className={`status status-${value}`}>{statusLabel(value)}</span>;
}
