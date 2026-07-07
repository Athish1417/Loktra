import { useState } from "react";
import { Loader2, MailCheck } from "lucide-react";
import Modal from "./ui/Modal";
import { forgotPassword } from "../api/auth";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function ForgotPasswordModal({ open, onClose }) {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);

  function close() {
    setEmail(""); setError(""); setDone(false); setBusy(false);
    onClose();
  }

  async function submit(e) {
    e.preventDefault();
    if (!EMAIL_RE.test(email)) {
      setError("Enter a valid email address.");
      return;
    }
    setError("");
    setBusy(true);
    try {
      await forgotPassword(email);
    } catch {
      // Placeholder endpoint never errors meaningfully; always show the generic message.
    } finally {
      setBusy(false);
      setDone(true);
    }
  }

  return (
    <Modal open={open} onClose={close} title="Reset your password">
      {done ? (
        <div className="flex items-start gap-3 py-2">
          <MailCheck className="mt-0.5 h-5 w-5 shrink-0 text-success" />
          <p className="text-sm leading-relaxed text-body">
            If this email exists, password reset instructions will be sent.
          </p>
        </div>
      ) : (
        <form onSubmit={submit} className="space-y-4">
          <p className="text-sm text-muted">
            Enter your account email and we'll send reset instructions.
          </p>
          <div>
            <label className="label">Email</label>
            <input
              className="input"
              type="email"
              autoFocus
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
            {error && <p className="mt-1 text-xs font-500 text-emergency">{error}</p>}
          </div>
          <button className="btn-primary w-full" disabled={busy}>
            {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : "Send reset link"}
          </button>
        </form>
      )}
    </Modal>
  );
}
