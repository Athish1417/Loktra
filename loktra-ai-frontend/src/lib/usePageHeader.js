import { useEffect } from "react";
import { useOutletContext } from "react-router-dom";

// Lets a page set the Topbar title/subtitle from the AppLayout outlet context.
export default function usePageHeader(title, subtitle) {
  const ctx = useOutletContext();
  useEffect(() => {
    ctx?.setHeader?.({ title, subtitle });
  }, [title, subtitle]); // eslint-disable-line react-hooks/exhaustive-deps
}
