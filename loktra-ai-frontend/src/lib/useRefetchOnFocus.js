import { useEffect, useRef } from "react";

/**
 * Re-run `fn` whenever the tab/window regains focus, so a list reflects the
 * backend (the source of truth) after another role updates a complaint. Kept
 * lightweight on purpose: no polling interval, fires only on focus / tab
 * visibility change. `fn` may change between renders without re-binding.
 */
export default function useRefetchOnFocus(fn) {
  const ref = useRef(fn);
  ref.current = fn;
  useEffect(() => {
    const run = () => {
      if (document.visibilityState === "visible") ref.current?.();
    };
    window.addEventListener("focus", run);
    document.addEventListener("visibilitychange", run);
    return () => {
      window.removeEventListener("focus", run);
      document.removeEventListener("visibilitychange", run);
    };
  }, []);
}
