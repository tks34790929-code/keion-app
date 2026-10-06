import { ApiError, createReservation, fetchReservations, type Reservation, type ReservationKind } from "./api";
import "./style.css";

const OPEN_MINUTES = 7 * 60; // 7:00
const CLOSE_MINUTES = 22 * 60; // 22:00
const SLOT_MINUTES = 10;

const KIND_LABELS: Record<ReservationKind, string> = {
  individual: "個人練",
};

// id で要素を取り出す。見つからないときは HTML の書き間違いなので、すぐに気付けるようエラーにする
function byId<T extends HTMLElement>(id: string): T {
  const el = document.getElementById(id);
  if (!el) throw new Error(`#${id} が見つかりません`);
  return el as T;
}

const dateInput = byId<HTMLInputElement>("date");
const list = byId<HTMLUListElement>("reservation-list");
const listMessage = byId<HTMLParagraphElement>("list-message");
const form = byId<HTMLFormElement>("reserve-form");
const formDate = byId<HTMLSpanElement>("form-date");
const nameInput = byId<HTMLInputElement>("name");
const startSelect = byId<HTMLSelectElement>("start-time");
const endSelect = byId<HTMLSelectElement>("end-time");
const submitButton = byId<HTMLButtonElement>("submit");
const formMessage = byId<HTMLParagraphElement>("form-message");

// 今日の日付（日本時間）を "2026-10-09" の形で返す。
// "sv-SE"（スウェーデン）の日付の書き方がちょうど YYYY-MM-DD なので使っている
function todayInTokyo(): string {
  return new Intl.DateTimeFormat("sv-SE", { timeZone: "Asia/Tokyo" }).format(new Date());
}

function toHHMM(minutes: number): string {
  const h = String(Math.floor(minutes / 60)).padStart(2, "0");
  const m = String(minutes % 60).padStart(2, "0");
  return `${h}:${m}`;
}

// 10分刻みの時刻を select の選択肢にする
function fillTimeOptions(select: HTMLSelectElement, from: number, to: number, selected: number): void {
  for (let t = from; t <= to; t += SLOT_MINUTES) {
    const option = new Option(toHHMM(t), toHHMM(t));
    option.selected = t === selected;
    select.add(option);
  }
}

function showMessage(el: HTMLElement, text: string, isError: boolean): void {
  el.textContent = text;
  el.classList.toggle("error", isError);
}

function formatDate(date: string): string {
  const [y, m, d] = date.split("-").map(Number);
  const weekday = "日月火水木金土"[new Date(y, m - 1, d).getDay()];
  return `${m}/${d}（${weekday}）`;
}

function renderReservations(reservations: Reservation[]): void {
  list.replaceChildren();
  for (const r of reservations) {
    const li = document.createElement("li");
    const time = document.createElement("span");
    time.className = "time";
    time.textContent = `${r.start_time.slice(0, 5)}〜${r.end_time.slice(0, 5)}`;
    const kind = document.createElement("span");
    kind.className = "kind";
    kind.textContent = KIND_LABELS[r.kind];
    const name = document.createElement("span");
    name.className = "name";
    // 名前は利用者が入力した文字なので、HTML として解釈されないよう textContent で入れる
    name.textContent = r.name;
    li.append(time, kind, name);
    list.append(li);
  }
  showMessage(listMessage, reservations.length === 0 ? "予約はありません" : "", false);
}

async function loadReservations(): Promise<void> {
  const date = dateInput.value;
  formDate.textContent = formatDate(date);
  try {
    const reservations = await fetchReservations(date);
    // 読み込み中に別の日が選ばれていたら、古い結果は表示しない
    if (date !== dateInput.value) return;
    renderReservations(reservations);
  } catch (e) {
    list.replaceChildren();
    showMessage(listMessage, e instanceof ApiError ? e.message : "予約状況を読み込めませんでした", true);
  }
}

async function submitReservation(event: SubmitEvent): Promise<void> {
  event.preventDefault(); // フォーム送信でページが再読み込みされないようにする
  submitButton.disabled = true; // 二重送信を防ぐ
  showMessage(formMessage, "", false);
  try {
    const r = await createReservation({
      name: nameInput.value,
      date: dateInput.value,
      start_time: startSelect.value,
      end_time: endSelect.value,
    });
    showMessage(
      formMessage,
      `${formatDate(r.date)} ${r.start_time.slice(0, 5)}〜${r.end_time.slice(0, 5)} に予約しました`,
      false,
    );
    await loadReservations();
  } catch (e) {
    showMessage(formMessage, e instanceof ApiError ? e.message : "予約できませんでした", true);
  } finally {
    submitButton.disabled = false;
  }
}

function main(): void {
  dateInput.value = todayInTokyo();
  // 開始は 7:00〜21:50、終了は 7:10〜22:00 から選ぶ
  fillTimeOptions(startSelect, OPEN_MINUTES, CLOSE_MINUTES - SLOT_MINUTES, 18 * 60);
  fillTimeOptions(endSelect, OPEN_MINUTES + SLOT_MINUTES, CLOSE_MINUTES, 19 * 60);

  dateInput.addEventListener("change", () => {
    if (!dateInput.value) return; // 日付が消されたときは何もしない
    showMessage(formMessage, "", false);
    void loadReservations();
  });
  form.addEventListener("submit", (event) => void submitReservation(event));

  void loadReservations();
}

main();
