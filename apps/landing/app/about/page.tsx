import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About",
};

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-16 md:px-6">
      <h1 className="text-4xl font-semibold">About Next-IoT</h1>
      <p className="mt-6 text-slate-600 leading-relaxed">
        Next-IoT dibangun untuk tim operasional di Indonesia yang membutuhkan platform IoT komersial lengkap —
        dari provisioning device, MQTT aman, automation, hingga billing dan dukungan lokal.
      </p>
    </div>
  );
}
