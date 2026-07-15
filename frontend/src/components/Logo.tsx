import abnLogo from "../assets/abn-logo.png";

type LogoProps = {
  compact?: boolean;
};

export default function Logo({ compact = false }: LogoProps) {
  return (
    <div className="logo-wrap" aria-label="Alpha Business Network">
      <img className="logo-mark" src={abnLogo} alt="" />
      {!compact && (
        <div>
          <strong>Alpha Business Network</strong>
          <span>Event Registration</span>
        </div>
      )}
    </div>
  );
}
