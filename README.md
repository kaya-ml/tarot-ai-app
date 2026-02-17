# AI Tarot Fortune

## Overview
Google Cloud Functions と Gemini API を活用した、サーバーレスなタロット占いシステムです。
WordPressで作成した自身のWebサイト上で、実際にサービスとして公開・運用しています。



## Features
- **サーバーレス構成**: Google Cloud Functionsを使用し、運用コストの最適化とスケーラビリティを確保。
- **Gemini API 連携**: LLM（Gemini 2.0 Flash-lite）を用いた、文脈に応じた深いリーディング。
- **多様なスプレッド対応**: ワンオラクルからケルト十字まで、計8種類の本格的なスプレッドを実装。
- **CORSセキュリティ**: 特定のオリジンからのリクエストのみを許可するセキュリティ設定を実装。

## System Architecture
システム全体の流れは以下の通りです。

[User / WordPress] 
      ↓ (1. 悩みとスプレッドをPOST)
[Google Cloud Functions (Python)]
      ↓ (2. プロンプトとカード情報を送信)
[Gemini API]
      ↓ (3. 占いのアドバイスを返却)
[Google Cloud Functions]
      ↓ (4. 最終的な結果をレスポンス)
[WordPress (JSで画面描画)]

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
└── README.md
```

## Challenges & Learning
- **プロンプトエンジニアリング**: 占いの結果が単なる文字列の羅列にならず、柔らかい表現や行動をポジティブに促すコメントを返すよう細かく設定しました。
- **運用を意識した開発**: サーバー費用を最小限に抑えるため、サーバーレス（FaaS）を選択しました。

## Author
運用中のURL:https://fortunes-for-you.com/ai-tarot-reading/
