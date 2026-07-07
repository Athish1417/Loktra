import logoUrl from "../../assets/loktra-logo.svg";

// Loktra brand mark: a location pin + green check (civic verification), in the
// brand's blue / green / saffron. `light` flips the wordmark for dark surfaces.
export default function Logo({ size = 28, light = false }) {
  const color = light ? "#fff" : "#12172E";
  return (
    <div className="flex items-center gap-2.5">
      <img
        src={logoUrl}
        alt="Loktra"
        width={size}
        height={size}
        className="shrink-0"
      />
      <div className="leading-none">
        <div
          className="font-display text-[17px] font-700 tracking-tight"
          style={{ color }}
        >
          Loktra
        </div>
      </div>
    </div>
  );
}
