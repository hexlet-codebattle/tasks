import { defineConfig } from 'vite';
import fs from 'fs/promises';
import path from 'path';

export default defineConfig({
  server: {
    port: 5173,
  },
  plugins: [
    {
      name: 'tasks-api',
      configureServer(server) {
        server.middlewares.use('/api/tasks.json', async (req, res, next) => {
          if (req.method === 'GET') {
            try {
              const releaseDir = path.resolve(process.cwd(), '..', 'release');
              const tasks = [];

              async function scanDirectory(dir) {
                const entries = await fs.readdir(dir, { withFileTypes: true });

                for (const entry of entries) {
                  const fullPath = path.join(dir, entry.name);

                  if (entry.isDirectory()) {
                    await scanDirectory(fullPath);
                  } else if (entry.name.endsWith('.json')) {
                    try {
                      const content = await fs.readFile(fullPath, "utf8");
                      const data = JSON.parse(content);
                      tasks.push({
                        ...data,
                        meta: {
                          name: data.name,
                          level: data.level,
                          tags: data.tags || [],
                          time_to_solve_sec: data.time_to_solve_sec,
                        },
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

              // Sort tasks by level and name
              tasks.sort((a, b) => {
                const levelOrder = { easy: 1, elementary: 2, medium: 3, hard: 4 };
                const aLevel = levelOrder[a.level] || 999;
                const bLevel = levelOrder[b.level] || 999;
                if (aLevel !== bLevel) return aLevel - bLevel;
                return a.name.localeCompare(b.name);
              });

              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify(tasks));
            } catch (e) {
              console.error('API Error:', e);
              res.statusCode = 500;
              res.end(JSON.stringify({ error: String(e) }));
            }
          } else {
            next();
          }
        });
      },
    },
  ],
});
