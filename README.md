# AI Tarot Fortune

## Overview
Google Cloud Functions と Gemini API を活用した、サーバーレスなタロット占いシステムです。
WordPressで構築された自身のWebサイト上で、実際にサービスとして公開・運用しています。



## Features
- **サーバーレス構成**: Google Cloud Functionsを採用し、運用コストの最適化とスケーラビリティを確保。
- **Gemini API 連携**: 最新のLLM（Gemini 2.0 Flash-lite）を用いた、文脈に応じた深いリーディング。
- **多様なスプレッド対応**: ワンオラクルからケルト十字まで、計8種類の本格的なスプレッドを実装。
- **CORSセキュリティ**: 特定のオリジンからのリクエストのみを許可するセキュリティ設定を実装。

## System Architecture
システム全体の流れは以下の通りです。

1. **Front-end (WordPress/JS)**: ユーザーの悩みとスプレッドを受け取り、APIへPOST。
2. **Back-end (Cloud Functions/Python)**: 
   - 78枚のカードデータからランダムにドロー（正逆位置判定含む）。
   - 引かれたカードの情報を元にGemini用プロンプトを生成。
3. **AI (Gemini API)**: プロンプトに基づき、寄り添いのあるアドバイスを生成。
4. **Response**: 最終的な占い結果をフロントエンドへ返し、画面に動的に描画。

## Tech Stack
- **Languages**: Python 3.12, JavaScript (ES6+)
- **Cloud**: Google Cloud Functions
- **AI**: Google Gemini API
- **Others**: Flask, WordPress, JSON

## Project Structure
```text
ai-tarot-api/
├── main.py                # バックエンドロジック (Cloud Functions)
├── requirements.txt       # 依存ライブラリ
├── tarot_cards.json       # タロットカード・マスターデータ (78枚)
├── tarot-api.js           # フロントエンドAPI連携ロジック
└── README.md              # 本ドキュメント
