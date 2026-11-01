"use client";

import { useEffect, useRef } from "react";

import { FadeInPage } from "@/components/motion/FadeInPage";
import { getApiBaseUrl } from "@/lib/auth/api";

export default function DeveloperDocsPage() {
  const hostRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const specUrl = `${getApiBaseUrl()}/api/v1/openapi.json`;
    const script = document.createElement("script");
    script.src = "https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js";
    script.async = true;
    script.onload = () => {
      const redoc = (window as Window & { Redoc?: { init: (url: string, opts: object, el: HTMLElement) => void } }).Redoc;
      if (redoc && hostRef.current) {
        redoc.init(specUrl, { theme: { colors: { primary: { main: "#2563eb" } } } }, hostRef.current);
      }
    };
    document.body.appendChild(script);
    return () => {
      script.remove();
    };
  }, []);

  return (
    <FadeInPage>
      <div ref={hostRef} className="min-h-[70vh] bg-background px-2 py-4 md:px-4" />
    </FadeInPage>
  );
}
