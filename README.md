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

3. DB のテーブルを作る（マイグレーション）。別のターミナルで実行する

   ```powershell
   docker compose exec backend alembic upgrade head
   ```

   まだ適用していないマイグレーション（`backend/alembic/versions/`）を最新まで適用する。
   main を取り込んでマイグレーションが増えたときも、もう一度実行する。

4. ブラウザで http://localhost:5173 を開き、練習室予約の画面が表示されることを確認する

ソースを保存すると自動で反映される（backend は再起動、frontend は画面が更新される）。

## テスト

バックエンドのテストは、同じ MySQL コンテナの中のテスト用データベース（`<MYSQL_DATABASE>_test`、標準は `keion_test`）で行う。
テストを始めるたびにテーブルを作り直すので、開発用データベースのデータには影響しない。

1. テスト用データベースを作る（初回のみ）

   DB のデータが空の状態で起動したときは自動で作られる。Sprint 0 の時点から DB のデータが残っている場合は、次のコマンドで作る。

   ```powershell
   docker compose exec db sh /docker-entrypoint-initdb.d/01-create-test-db.sh
   ```

2. テストを実行する

   ```powershell
   docker compose exec backend pytest
   ```

   `-v` を付けるとテストを1件ずつ表示する。

## よく使うコマンド

| やりたいこと | コマンド |
|---|---|
| 状態を見る | `docker compose ps` |
| ログを見る | `docker compose logs -f backend`（`-f` は流し続ける。Ctrl+C で終了） |
| 停止する | `docker compose down`（DB のデータは残る） |
| DB のデータも消して停止する | `docker compose down -v` |
| マイグレーションを作る（モデルを変えたとき） | `docker compose exec backend alembic revision --autogenerate -m "説明"`（作られたファイルは必ず中身を確認する） |

## 注意

- **DB のパスワードを変えたとき**: MySQL は最初に起動したときのパスワードでデータを作るため、`.env` を変えただけでは反映されない。
  `docker compose down -v` で DB のデータを消してから起動し直す。
- **frontend のパッケージを追加・更新したとき**: `node_modules` はコンテナ側のボリュームに残るため、
  `docker compose up --build -V` で作り直す（`-V` はボリュームを新しくするオプション）。
- **ディスク容量**: 3つのイメージで約 2 GB 使う。不要になったイメージは `docker image prune` で削除できる。
