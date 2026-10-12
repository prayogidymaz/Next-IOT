import type { MetadataRoute } from "next";

import { SITE_URL, USE_CASES } from "@/lib/site";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = SITE_URL.replace(/\/$/, "");
  const staticRoutes = ["", "/pricing", "/features", "/about", "/contact", "/docs"];
  const useCases = Object.keys(USE_CASES).map((slug) => `/use-cases/${slug}`);
  return [...staticRoutes, ...useCases].map((path) => ({
    url: `${base}${path}`,
    lastModified: new Date(),
    changeFrequency: path === "" ? "weekly" : "monthly",
    priority: path === "" ? 1 : 0.7,
  }));
}
