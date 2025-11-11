import React from "react";
import { createRoot } from "react-dom/client";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

function TaskDescriptionMarkdown({ children }) {
  return (
    <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
      {children || ""}
    </ReactMarkdown>
  );
}

function Section({ title, children }) {
  return (
    <section
      style={{
        border: "1px solid #eee",
        borderRadius: 12,
        padding: 16,
        margin: "12px 0",
      }}
    >
      <h2>{title}</h2>
      <div>{children}</div>
    </section>
  );
}

function TaskCard({ task }) {
  const {
    name,
    level,
    tags,
    time_to_solve_sec,
    description_en,
    description_ru,
    limits,
    examples,
    input_signature,
    output_signature,
    solution,
    asserts,
  } = task;

  return (
    <div
      style={{
        border: "2px solid #ddd",
        borderRadius: 12,
        padding: 20,
        margin: "20px 0",
        backgroundColor: "#f9f9f9",
      }}
    >
      <h2 style={{ color: "#333", marginBottom: 12 }}>{name || "Task"}</h2>
      <div style={{ color: "#666", marginBottom: 16, fontSize: "14px" }}>
        <b>Level:</b> {level} • <b>Tags:</b> {(tags || []).join(", ")} •{" "}
        <b>Time:</b> {time_to_solve_sec}s
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 16,
          marginBottom: 16,
        }}
      >
        <Section title="Description (EN)">
          <TaskDescriptionMarkdown>{description_en}</TaskDescriptionMarkdown>
        </Section>
        <Section title="Описание (RU)">
          <TaskDescriptionMarkdown>{description_ru}</TaskDescriptionMarkdown>
        </Section>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 16,
          marginBottom: 16,
        }}
      >
        <Section title="Limits">
          <TaskDescriptionMarkdown>{limits}</TaskDescriptionMarkdown>
        </Section>
        <Section title="Examples">
          <TaskDescriptionMarkdown>
            {"```\n" + examples + "\n```"}
          </TaskDescriptionMarkdown>
        </Section>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 16,
          marginBottom: 16,
        }}
      >
        <Section title="Input Signature">
          <pre
            style={{
              backgroundColor: "#f5f5f5",
              padding: 12,
              borderRadius: 8,
              overflow: "auto",
            }}
          >
            {JSON.stringify(input_signature, null, 2)}
          </pre>
        </Section>
        <Section title="Output Signature">
          <pre
            style={{
              backgroundColor: "#f5f5f5",
              padding: 12,
              borderRadius: 8,
              overflow: "auto",
            }}
          >
            {JSON.stringify(output_signature, null, 2)}
          </pre>
        </Section>
      </div>

      <Section title="Solution">
        <pre
          style={{
            backgroundColor: "#f5f5f5",
            padding: 12,
            borderRadius: 8,
            overflow: "auto",
            maxHeight: 400,
          }}
        >
          {solution}
        </pre>
      </Section>

      <Section title="Asserts">
        <pre
          style={{
            backgroundColor: "#f5f5f5",
            padding: 12,
            borderRadius: 8,
            overflow: "auto",
            maxHeight: 400,
          }}
        >
          {JSON.stringify(asserts, null, 2)}
        </pre>
      </Section>
    </div>
  );
}

function App() {
  const [tasks, setTasks] = React.useState(null);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    (async () => {
      try {
        const res = await fetch("/api/tasks.json");
        if (!res.ok) throw new Error(await res.text());
        const allTasks = await res.json();
        // Sort tasks by level and name
        allTasks.sort((a, b) => {
          const levelOrder = { easy: 1, elementary: 2, medium: 3, hard: 4 };
          const aLevel = levelOrder[a.level] || 999;
          const bLevel = levelOrder[b.level] || 999;
          if (aLevel !== bLevel) return aLevel - bLevel;
          return a.name.localeCompare(b.name);
        });
        setTasks(allTasks);
      } catch (e) {
        setError(String(e));
      }
    })();
  }, []);

  if (error) return <div>Error: {error}</div>;
  if (!tasks) return <div>Loading…</div>;

  return (
    <div
      style={{
        maxWidth: 1200,
        margin: "24px auto",
        fontFamily:
          "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial",
      }}
    >
      <h1 style={{ textAlign: "center", marginBottom: 32, color: "#333" }}>
        All Tasks ({tasks.length})
      </h1>

      {tasks.map((task, index) => (
        <div key={`${task.name}-${index}`}>
          <TaskCard task={task} />
          {index < tasks.length - 1 && (
            <hr
              style={{
                border: "none",
                borderTop: "2px solid #eee",
                margin: "20px 0",
              }}
            />
          )}
        </div>
      ))}
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
