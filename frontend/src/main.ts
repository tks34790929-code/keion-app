type HelloResponse = { message: string; now: string };
type DbHealthResponse = { db: string };

function show(id: string, text: string): void {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return (await res.json()) as T;
}

async function main(): Promise<void> {
  try {
    const hello = await getJson<HelloResponse>("/api/hello");
    show("message", hello.message);
    show("now", hello.now);
  } catch (e) {
    show("message", `エラー: ${String(e)}`);
    show("now", "-");
  }

  try {
    const health = await getJson<DbHealthResponse>("/api/health/db");
    show("db", health.db);
  } catch (e) {
    show("db", `エラー: ${String(e)}`);
  }
}

main();
