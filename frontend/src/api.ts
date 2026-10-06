// バックエンド API を呼ぶ関数と、やり取りするデータの型

export type ReservationKind = "individual";

export type Reservation = {
  id: number;
  kind: ReservationKind;
  name: string;
  date: string; // "2026-10-09"
  start_time: string; // "15:10:00"
  end_time: string;
};

export type ReservationInput = {
  name: string;
  date: string;
  start_time: string; // "15:10"
  end_time: string;
};

// API がエラーを返したときの例外。message に画面に出す理由が入る
export class ApiError extends Error {}

async function errorMessage(res: Response): Promise<string> {
  try {
    const body: unknown = await res.json();
    // バックエンドは { "detail": "理由" } の形で理由を返す
    if (typeof body === "object" && body !== null && "detail" in body && typeof body.detail === "string") {
      return body.detail;
    }
  } catch {
    // JSON でない応答のときは下の共通メッセージにする
  }
  return `エラーが発生しました（${res.status}）`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init);
  if (!res.ok) throw new ApiError(await errorMessage(res));
  return (await res.json()) as T;
}

export function fetchReservations(date: string): Promise<Reservation[]> {
  return request(`/api/reservations?date=${encodeURIComponent(date)}`);
}

export function createReservation(input: ReservationInput): Promise<Reservation> {
  return request("/api/reservations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}
