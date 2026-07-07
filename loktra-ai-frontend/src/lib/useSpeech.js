import { useEffect, useRef, useState } from "react";

// Thin wrapper over the browser Web Speech API (Chrome/Edge). Returns transcript
// chunks via onResult. Gracefully reports unsupported browsers.
export default function useSpeech(lang = "en-IN", onResult) {
  const [listening, setListening] = useState(false);
  const [supported, setSupported] = useState(true);
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SR =
      window.SpeechRecognition || window.webkitSpeechRecognition || null;
    if (!SR) {
      setSupported(false);
      return;
    }
    const rec = new SR();
    rec.continuous = true;
    rec.interimResults = false;
    rec.lang = lang;
    rec.onresult = (e) => {
      let text = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        text += e.results[i][0].transcript;
      }
      if (text) onResult?.(text.trim());
    };
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);
    recognitionRef.current = rec;
    return () => {
      try {
        rec.stop();
      } catch {
        /* noop */
      }
    };
  }, [lang]); // eslint-disable-line react-hooks/exhaustive-deps

  const toggle = () => {
    const rec = recognitionRef.current;
    if (!rec) return;
    if (listening) {
      rec.stop();
      setListening(false);
    } else {
      try {
        rec.lang = lang;
        rec.start();
        setListening(true);
      } catch {
        /* already started */
      }
    }
  };

  return { listening, supported, toggle };
}
