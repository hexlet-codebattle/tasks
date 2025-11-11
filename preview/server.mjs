#!/usr/bin/env node
import fs from "node:fs/promises";
import fssync from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import express from "express";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = process.env.PORT || 5173;

async function loadAllJsonFiles() {
  const releaseDir = path.resolve(__dirname, "..", "release");
  const tasks = [];

  async function scanDirectory(dir) {
    const entries = await fs.readdir(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        await scanDirectory(fullPath);
      } else if (entry.name.endsWith(".json")) {
        try {
          const content = await fs.readFile(fullPath, "utf8");
          const data = JSON.parse(content);
          tasks.push({
            ...data,
            meta: {
              name: data.name,
              solution: data.solution || "",
              level: data.level,
              tags: data.tags || [],
              time_to_solve_sec: data.time_to_solve_sec,
            },
            solution: data.solution || "",
            description_en: data.description_en || "",
            description_ru: data.description_ru || "",
            examples: data.examples || "",
            limits: data.limits || "",
          });
        } catch (e) {
          console.error(`Error loading ${fullPath}:`, e);
        }
      }
    }
  }

  await scanDirectory(releaseDir);
  return tasks;
}

async function main() {
  const app = express();

  // API endpoint for tasks
  app.get("/tasks.json", async (_req, res) => {
    try {
      res.json(await loadAllJsonFiles());
    } catch (e) {
      res.status(500).json({ error: String(e) });
    }
  });

  // Serve static files from public directory
  app.use(express.static(path.join(__dirname, "public")));

  // Vite in middleware mode for development
  const { createServer } = await import("vite");
  const vite = await createServer({
    root: __dirname,
    server: { middlewareMode: true },
  });

  // Use vite middlewares for React app
  app.use(vite.middlewares);

  app.listen(PORT, () => {
    console.log(`\n🔍 Preview running: http://localhost:${PORT}`);
    console.log(`📄 Showing all tasks from release directory\n`);
  });
}

main();
