import { Loader2 } from "lucide-react";

export default function Loader({ full = false, label = "Loading" }) {
  const spinner = (
    <div className="flex flex-col items-center gap-3 text-muted">
      <Loader2 className="h-6 w-6 animate-spin text-royal" />
      <span className="text-sm font-medium">{label}…</span>
    </div>
  );
  if (full) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-paper">
        {spinner}
      </div>
    );
  }
  return <div className="flex items-center justify-center py-16">{spinner}</div>;
}
