import { useEffect, useState } from "react";
import { priorityColor, priorityLabel } from "../../lib/constants";

// A 270° arc gauge. `size` controls diameter. Animates the fill on mount.
export default function PriorityGauge({ score = 0, size = 132, showLabel = true }) {
  const [display, setDisplay] = useState(0);
  const stroke = 11;
  const r = (size - stroke) / 2;
  const cx = size / 2;
  const cy = size / 2;
  const startAngle = 135; // degrees
  const sweep = 270;
  const circumference = 2 * Math.PI * r;
  const arcLen = (sweep / 360) * circumference;
  const color = priorityColor(score);

  // Count-up + arc fill animation.
  useEffect(() => {
    let raf;
    const start = performance.now();
    const dur = 900;
    const tick = (now) => {
      const t = Math.min(1, (now - start) / dur);
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay(Math.round(eased * score));
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [score]);

  const pct = Math.max(0, Math.min(100, display)) / 100;
  const dash = `${arcLen * pct} ${circumference}`;

  const polar = (angleDeg) => {
    const a = (angleDeg * Math.PI) / 180;
    return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
  };
  const [sx, sy] = polar(startAngle);
  const [ex, ey] = polar(startAngle + sweep);
  const largeArc = sweep > 180 ? 1 : 0;
  const trackPath = `M ${sx} ${sy} A ${r} ${r} 0 ${largeArc} 1 ${ex} ${ey}`;

  return (
    <div
      className="relative inline-flex items-center justify-center"
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} className="-rotate-0">
        {/* track */}
        <path
          d={trackPath}
          fill="none"
          stroke="#EEF0F5"
          strokeWidth={stroke}
          strokeLinecap="round"
        />
        {/* value arc */}
        <path
          d={trackPath}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={dash}
          style={{ transition: "stroke 0.3s" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span
          className="font-display font-700 tabular leading-none"
          style={{ fontSize: size * 0.3, color }}
        >
          {display}
        </span>
        {showLabel && (
          <span className="mt-1 text-[10px] font-600 uppercase tracking-wider text-muted">
            {priorityLabel(score)}
          </span>
        )}
      </div>
    </div>
  );
}
