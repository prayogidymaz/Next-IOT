import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Contact",
};

export default function ContactPage() {
  return (
    <div className="mx-auto max-w-xl px-4 py-16 md:px-6">
      <h1 className="text-4xl font-semibold">Contact</h1>
      <p className="mt-3 text-slate-600">Book demo atau pertanyaan enterprise — kami balas dalam 1×24 jam kerja.</p>
      <form className="mt-8 space-y-4">
        <label className="block text-sm">
          <span className="text-slate-600">Email</span>
          <input type="email" required className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2" />
        </label>
        <label className="block text-sm">
          <span className="text-slate-600">Message</span>
          <textarea rows={4} className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2" />
        </label>
        <button type="submit" className="rounded-md bg-slate-900 px-4 py-2.5 text-sm font-medium text-white">
          Send
        </button>
      </form>
    </div>
  );
}
