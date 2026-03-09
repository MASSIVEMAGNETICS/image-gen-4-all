"use client";

import { useState, useCallback, useEffect } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// Maximum number of gallery entries to keep in localStorage
const GALLERY_MAX_SIZE = 20;

// Maximum characters shown in a preset button label before truncation
const MAX_PRESET_LABEL_LENGTH = 28;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface GenerateResponse {
  image_b64: string;
  width: number;
  height: number;
  seed: number;
  prompt: string;
  latency_ms: number;
}

interface GalleryEntry extends GenerateResponse {
  id: string;
  zoom: number;
  timestamp: number;
}

// ---------------------------------------------------------------------------
// Preset prompts
// ---------------------------------------------------------------------------

const PRESETS = [
  "a face made of trees under a galaxy",
  "an ocean of gravitational waves",
  "fractal forest at dawn",
  "cosmic nebula forming stars",
  "portrait in Turing patterns",
  "abstract mandala in deep space",
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function uid(): string {
  return Math.random().toString(36).slice(2, 9);
}

function loadGallery(): GalleryEntry[] {
  try {
    const raw = localStorage.getItem("hart_gallery");
    return raw ? (JSON.parse(raw) as GalleryEntry[]) : [];
  } catch {
    return [];
  }
}

function saveGallery(entries: GalleryEntry[]): void {
  try {
    localStorage.setItem("hart_gallery", JSON.stringify(entries.slice(0, GALLERY_MAX_SIZE)));
  } catch {
    // storage unavailable — ignore
  }
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function Spinner() {
  return (
    <svg
      className="animate-spin h-5 w-5 text-white"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-label="Loading"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v8H4z"
      />
    </svg>
  );
}

function Badge({ label, value }: { label: string; value: string | number }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-zinc-800 px-2 py-0.5 text-xs text-zinc-300">
      <span className="text-zinc-500">{label}</span>
      {value}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export default function Home() {
  const [prompt, setPrompt] = useState(PRESETS[0]);
  const [zoom, setZoom] = useState(2);
  const [seedInput, setSeedInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [current, setCurrent] = useState<GenerateResponse | null>(null);
  const [gallery, setGallery] = useState<GalleryEntry[]>([]);
  const [selected, setSelected] = useState<GalleryEntry | null>(null);
  const [apiHealthy, setApiHealthy] = useState<boolean | null>(null);

  // Load gallery from localStorage on mount
  useEffect(() => {
    setGallery(loadGallery());
  }, []);

  // Health check on mount
  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((r) => setApiHealthy(r.ok))
      .catch(() => setApiHealthy(false));
  }, []);

  const handleGenerate = useCallback(async () => {
    setError(null);
    setLoading(true);
    setSelected(null);

    const seed =
      seedInput.trim() !== "" ? parseInt(seedInput.trim(), 10) : undefined;

    try {
      const res = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, zoom, seed: seed ?? null }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(
          (data as { detail?: string }).detail ?? `HTTP ${res.status}`
        );
      }

      const data: GenerateResponse = await res.json();
      setCurrent(data);

      const entry: GalleryEntry = {
        ...data,
        id: uid(),
        zoom,
        timestamp: Date.now(),
      };

      setGallery((prev) => {
        const next = [entry, ...prev].slice(0, GALLERY_MAX_SIZE);
        saveGallery(next);
        return next;
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [prompt, zoom, seedInput]);

  const displayed = selected ?? current;

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      {/* Header */}
      <header className="border-b border-zinc-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">
            HART-Morphosis
          </h1>
          <p className="text-xs text-zinc-500 mt-0.5">
            Nature doesn&apos;t store images — it grows them.
          </p>
        </div>
        <span
          className={`text-xs px-2 py-1 rounded-full font-mono ${
            apiHealthy === null
              ? "bg-zinc-800 text-zinc-500"
              : apiHealthy
              ? "bg-emerald-900 text-emerald-400"
              : "bg-red-900 text-red-400"
          }`}
        >
          {apiHealthy === null ? "checking…" : apiHealthy ? "API online" : "API offline"}
        </span>
      </header>

      <div className="mx-auto max-w-6xl px-6 py-8 flex flex-col lg:flex-row gap-8">
        {/* Left column — controls */}
        <aside className="w-full lg:w-80 flex-shrink-0 space-y-6">
          {/* Prompt */}
          <div>
            <label className="block text-sm font-medium mb-1">Prompt</label>
            <textarea
              className="w-full rounded-lg bg-zinc-900 border border-zinc-700 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              rows={3}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the image…"
            />
          </div>

          {/* Presets */}
          <div>
            <p className="text-xs text-zinc-500 mb-2">Presets</p>
            <div className="flex flex-wrap gap-1.5">
              {PRESETS.map((p) => (
                <button
                  key={p}
                  onClick={() => setPrompt(p)}
                  className={`text-xs rounded-full px-2.5 py-1 border transition-colors ${
                    prompt === p
                      ? "border-indigo-500 bg-indigo-900 text-indigo-300"
                      : "border-zinc-700 bg-zinc-900 text-zinc-400 hover:border-zinc-500"
                  }`}
                >
                  {p.length > MAX_PRESET_LABEL_LENGTH
                    ? p.slice(0, MAX_PRESET_LABEL_LENGTH - 1) + "…"
                    : p}
                </button>
              ))}
            </div>
          </div>

          {/* Zoom */}
          <div>
            <label className="flex items-center justify-between text-sm font-medium mb-1">
              <span>Zoom level</span>
              <span className="font-mono text-indigo-400">{zoom}×</span>
            </label>
            <input
              type="range"
              min={1}
              max={6}
              value={zoom}
              onChange={(e) => setZoom(Number(e.target.value))}
              className="w-full accent-indigo-500"
            />
            <div className="flex justify-between text-xs text-zinc-600 mt-0.5">
              <span>1×</span>
              <span>6×</span>
            </div>
          </div>

          {/* Seed */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Seed{" "}
              <span className="text-zinc-500 font-normal">(optional)</span>
            </label>
            <input
              type="number"
              className="w-full rounded-lg bg-zinc-900 border border-zinc-700 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Random"
              value={seedInput}
              onChange={(e) => setSeedInput(e.target.value)}
            />
          </div>

          {/* Generate button */}
          <button
            onClick={handleGenerate}
            disabled={loading || !prompt.trim()}
            className="w-full flex items-center justify-center gap-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed px-4 py-3 text-sm font-semibold transition-colors"
          >
            {loading ? <Spinner /> : null}
            {loading ? "Growing…" : "Generate"}
          </button>

          {error && (
            <p className="text-sm text-red-400 bg-red-950 rounded-lg px-3 py-2">
              {error}
            </p>
          )}
        </aside>

        {/* Right column — image + gallery */}
        <main className="flex-1 space-y-6">
          {/* Current image */}
          <div className="rounded-xl border border-zinc-800 bg-zinc-900 overflow-hidden">
            {displayed ? (
              <>
                <img
                  src={`data:image/png;base64,${displayed.image_b64}`}
                  alt={displayed.prompt}
                  className="w-full object-contain"
                  style={{ imageRendering: "pixelated" }}
                />
                <div className="px-4 py-3 flex flex-wrap gap-2 border-t border-zinc-800">
                  <Badge label="seed" value={displayed.seed} />
                  <Badge label="size" value={`${displayed.width}×${displayed.height}`} />
                  {"latency_ms" in displayed && (
                    <Badge label="ms" value={Math.round(displayed.latency_ms)} />
                  )}
                  {"zoom" in displayed && (
                    <Badge label="zoom" value={`${(displayed as GalleryEntry).zoom}×`} />
                  )}
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center h-64 text-zinc-600 text-sm">
                {loading ? "Generating…" : "Your image will appear here"}
              </div>
            )}
          </div>

          {/* Gallery */}
          {gallery.length > 0 && (
            <section>
              <h2 className="text-sm font-medium text-zinc-400 mb-3">
                History ({gallery.length})
              </h2>
              <div className="grid grid-cols-4 sm:grid-cols-6 gap-2">
                {gallery.map((entry) => (
                  <button
                    key={entry.id}
                    onClick={() => setSelected(entry)}
                    title={entry.prompt}
                    className={`aspect-square rounded-lg overflow-hidden border-2 transition-colors ${
                      selected?.id === entry.id
                        ? "border-indigo-500"
                        : "border-transparent hover:border-zinc-600"
                    }`}
                  >
                    <img
                      src={`data:image/png;base64,${entry.image_b64}`}
                      alt={entry.prompt}
                      className="w-full h-full object-cover"
                      style={{ imageRendering: "pixelated" }}
                    />
                  </button>
                ))}
              </div>
            </section>
          )}
        </main>
      </div>

      <footer className="text-center text-xs text-zinc-700 py-6">
        HART-Morphosis · CC0 1.0 · Grow it. Share it. Own nothing.
      </footer>
    </div>
  );
}

