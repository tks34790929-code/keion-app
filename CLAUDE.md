# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

芝浦工業大学 軽音楽同好会向けの「練習室予約・バンド募集アプリ」。現在は Sprint 0（環境構築）段階。
仕様などのドキュメントは `docs/` にある（要件定義書: `docs/requirements.md`）。実装の前に必ず参照し、未決事項は勝手に決めずユーザーに確認する。

## 技術構成

- バックエンド: Python（FastAPI, SQLAlchemy, Alembic）
- フロントエンド: TypeScript + Vite
- DB: MySQL
- 実行環境: Docker Compose（ローカル）→ 将来は AWS（EC2 → RDS + S3 + CloudFront）
- 時刻は日本時間（Asia/Tokyo）で扱う

## 開発の進め方

- アジャイル（1週間スプリント）。タスクは GitHub Issues / Projects で管理
- 流れは Issue → ブランチ → PR → main へマージ。**main に直接コミットしない**
- ブランチ名は `種類/Issue番号-内容`（例: `feat/12-reservation-list`）
- コミットメッセージは日本語で、`feat:` / `fix:` / `docs:` / `chore:` などの接頭辞を付ける
- 複数ファイルにまたがる変更や設計に関わる変更は、実装前にプランを示してユーザーの承認を得る
- 秘密情報（`.env`、パスワード、AWS のアクセスキーなど）はコミットしない

## ユーザーへの対応

- 回答は日本語で行う
- ユーザーは C 言語の経験だけがある初学者。ファイルを変更するときは「何を・なぜ」変えるのかを日本語で説明する
- コマンドを実行するときは、そのコマンドとオプションが何をするのかも説明する
