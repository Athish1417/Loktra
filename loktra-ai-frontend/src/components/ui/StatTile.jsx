import { useEffect, useState } from "react";

// Compact metric tile with an animated count-up.
export default function StatTile({ icon: Icon, label, value, tone = "royal", suffix = "" }) {
  const [n, setN] = useState(0);
  const target = Number(value) || 0;

  useEffect(() => {
    let raf;
    const start = performance.now();
    const dur = 700;
    const tick = (now) => {
      const t = Math.min(1, (now - start) / dur);
      const eased = 1 - Math.pow(1 - t, 3);
      setN(eased * target);
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target]);

  const tones = {
    royal: "bg-royal-50 text-royal",
    saffron: "bg-saffron-100 text-saffron-600",
    emergency: "bg-emergency/10 text-emergency",
    success: "bg-success/10 text-success",
    ink: "bg-ink/5 text-ink",
  };
  const isFloat = !Number.isInteger(target);
  const shown = isFloat ? n.toFixed(1) : Math.round(n);

  return (
    <div className="card flex items-center gap-3.5 p-4">
      <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${tones[tone]}`}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="min-w-0">
        <p className="font-display text-2xl font-700 tabular leading-none text-body">
          {shown}
          {suffix}
        </p>
        <p className="mt-1 truncate text-xs font-500 text-muted">{label}</p>
      </div>
    </div>
  );
}
