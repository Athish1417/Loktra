import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Eye, EyeOff, Loader2 } from "lucide-react";
import Logo from "../components/ui/Logo";
import LocationCascade from "../components/LocationCascade";
import { useAuth, HOME_BY_ROLE } from "../context/AuthContext";
import { useToast } from "../components/ui/Toast";
import { errorMessage } from "../api/client";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const EMPTY = {
  name: "", email: "", password: "", confirm: "", phone: "",
  state_id: "", district_id: "", constituency_id: "", ward_id: "",
};

export default function Register() {
  const { register } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const [form, setForm] = useState(EMPTY);
  const [show, setShow] = useState(false);
  const [errors, setErrors] = useState({});
  const [busy, setBusy] = useState(false);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  const patch = (p) => setForm((f) => ({ ...f, ...p }));

  function validate() {
    const err = {};
    if (!form.name.trim()) err.name = "Full name is required.";
    if (!EMAIL_RE.test(form.email)) err.email = "Enter a valid email address.";
    if (form.password.length < 6) err.password = "Password must be at least 6 characters.";
    if (form.confirm !== form.password) err.confirm = "Passwords do not match.";
    if (!form.constituency_id) err.location = "Select your constituency.";
    setErrors(err);
    return Object.keys(err).length === 0;
  }

  async function submit(e) {
    e.preventDefault();
    if (!validate()) return;
    setBusy(true);
    try {
      const user = await register({
        name: form.name,
        email: form.email,
        password: form.password,
        phone: form.phone || null,
        // Residential/default location saved to the profile.
        home_state_id: form.state_id ? Number(form.state_id) : null,
        home_district_id: form.district_id ? Number(form.district_id) : null,
        home_constituency_id: form.constituency_id ? Number(form.constituency_id) : null,
        home_ward_id: form.ward_id ? Number(form.ward_id) : null,
      });
      toast.success(`Welcome, ${user.name.split(" ")[0]}`);
      navigate(HOME_BY_ROLE[user.role] || "/app", { replace: true });
    } catch (err) {
      toast.error(errorMessage(err, "Could not create your account."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-paper px-5 py-10">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-lg"
      >
        <div className="mb-6 flex justify-center">
          <Logo size={30} />
        </div>

        <div className="card p-6 sm:p-8">
          <h2 className="font-display text-2xl font-700 text-body">Create your account</h2>
          <p className="mt-1 text-sm text-muted">
            Register as a citizen to report and track civic issues.
          </p>

          <form onSubmit={submit} className="mt-6 space-y-4" noValidate>
            <div>
              <label className="label">Full name</label>
              <input className="input" value={form.name} onChange={set("name")} placeholder="Your name" />
              {errors.name && <p className="mt-1 text-xs font-500 text-emergency">{errors.name}</p>}
            </div>

            <div>
              <label className="label">Email</label>
              <input className="input" type="email" value={form.email} onChange={set("email")} placeholder="you@example.com" />
              {errors.email && <p className="mt-1 text-xs font-500 text-emergency">{errors.email}</p>}
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="label">Password</label>
                <div className="relative">
                  <input
                    className="input pr-10"
                    type={show ? "text" : "password"}
                    value={form.password}
                    onChange={set("password")}
                    placeholder="At least 6 characters"
                  />
                  <button
                    type="button"
                    onClick={() => setShow((s) => !s)}
                    className="absolute inset-y-0 right-0 flex items-center px-3 text-muted hover:text-body"
                    aria-label={show ? "Hide password" : "Show password"}
                  >
                    {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {errors.password && <p className="mt-1 text-xs font-500 text-emergency">{errors.password}</p>}
              </div>
              <div>
                <label className="label">Confirm password</label>
                <input
                  className="input"
                  type={show ? "text" : "password"}
                  value={form.confirm}
                  onChange={set("confirm")}
                  placeholder="Re-enter password"
                />
                {errors.confirm && <p className="mt-1 text-xs font-500 text-emergency">{errors.confirm}</p>}
              </div>
            </div>

            <div>
              <label className="label">Phone (optional)</label>
              <input className="input" value={form.phone} onChange={set("phone")} placeholder="+91…" />
            </div>

            <div>
              <p className="label">Residential location</p>
              <p className="mb-2 text-xs text-muted">
                Saved as your default — you won't need to re-enter it when reporting.
              </p>
              <LocationCascade value={form} onChange={patch} wardLabel="Ward / Village (optional)" />
              {errors.location && <p className="mt-1 text-xs font-500 text-emergency">{errors.location}</p>}
            </div>

            <button className="btn-primary w-full" disabled={busy}>
              {busy ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  Create account
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          <p className="mt-4 text-center text-sm text-muted">
            Already have an account?{" "}
            <Link to="/login" className="font-600 text-royal hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
