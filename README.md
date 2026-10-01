# keion-app

芝浦工業大学 軽音楽同好会向けの「練習室予約・バンド募集アプリ」。
仕様は [docs/requirements.md](docs/requirements.md) を参照。

## 構成

| サービス | 内容 | URL |
|---|---|---|
| frontend | Vite + TypeScript（`frontend/`） | http://localhost:5173 |
| backend | FastAPI（`backend/`） | http://localhost:8000/docs （API 仕様） |
| db | MySQL 8.4 | コンテナ内のみ（PC には公開しない） |

ブラウザは frontend にだけアクセスする。`/api` へのリクエストは Vite が backend に転送する。

## 必要なもの

- Docker Desktop

## 起動手順

1. 環境変数ファイルを作る（初回のみ）

   ```powershell
   Copy-Item .env.example .env
   ```

   必要に応じて `.env` のパスワードを書き換える。`.env` はコミットしない。

2. 起動する

   ```powershell
   docker compose up --build
   ```

   初回はイメージのダウンロードがあるため数分かかる。`-d` を付けるとバックグラウンドで起動する。

3. ブラウザで http://localhost:5173 を開き、API のメッセージ・時刻・`DB: ok` が表示されることを確認する

ソースを保存すると自動で反映される（backend は再起動、frontend は画面が更新される）。

## よく使うコマンド

| やりたいこと | コマンド |
|---|---|
| 状態を見る | `docker compose ps` |
| ログを見る | `docker compose logs -f backend`（`-f` は流し続ける。Ctrl+C で終了） |
| 停止する | `docker compose down`（DB のデータは残る） |
| DB のデータも消して停止する | `docker compose down -v` |

## 注意

- **DB のパスワードを変えたとき**: MySQL は最初に起動したときのパスワードでデータを作るため、`.env` を変えただけでは反映されない。
  `docker compose down -v` で DB のデータを消してから起動し直す。
- **frontend のパッケージを追加・更新したとき**: `node_modules` はコンテナ側のボリュームに残るため、
  `docker compose up --build -V` で作り直す（`-V` はボリュームを新しくするオプション）。
- **ディスク容量**: 3つのイメージで約 2 GB 使う。不要になったイメージは `docker image prune` で削除できる。
