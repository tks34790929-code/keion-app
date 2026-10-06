#!/bin/sh
# テスト用データベース（<開発用の名前>_test）を作り、アプリ用ユーザーに権限を与える。
#
# - MySQL の初回起動時（DB のデータが空のとき）に自動で実行される
# - 既に DB のデータがある場合は、次のコマンドで手動実行する（何度実行しても安全）
#     docker compose exec db sh /docker-entrypoint-initdb.d/01-create-test-db.sh
# - パスワードなどは MySQL コンテナの環境変数（compose.yaml で .env から渡している）を使う
set -eu

mysql -uroot -p"$MYSQL_ROOT_PASSWORD" <<SQL
CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}_test\`;
GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}_test\`.* TO '${MYSQL_USER}'@'%';
SQL

echo "テスト用データベース ${MYSQL_DATABASE}_test を準備しました"
