import functions_framework
from flask import request, jsonify
import json
import random
import google.generativeai as genai
import os


# ダミー設定、デプロイ時に実際のAPIキーを環境変数として渡す
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY_ENV", "YOUR_GEMINI_API_KEY_HERE_FOR_LOCAL_TEST")

# genai.configureは関数の外で一度だけ実行
genai.configure(api_key=GEMINI_API_KEY)

# geminiのモデル1.5終了、2.0へ変更-今後の動作不良時に要確認
GEMINI_MODEL_NAME = "models/gemini-2.0-flash-lite"

# タロットデータ読み込み
try:
    with open("tarot_cards.json", "r", encoding="utf-8") as f:
        tarot_cards = json.load(f)
except FileNotFoundError:
    # Cloud Functionsのログに出力
    print("Error: tarot_cards.json not found.")
    tarot_cards = [] 

# タロットスプレッドの定義
spreads = {
    "ワンオラクル (1枚引き / 質問に対して簡単かつ明確な答えが欲しい時)": {
        "num_cards": 1,
        "positions": ["回答"]
    },
    "Yes No (2枚引き / 質問に対するアドバイスとして、やると良い(Yes)事・やらない方が良い(No)事を提示)": {
        "num_cards": 2,
        "positions": ["Yesの場合", "Noの場合"]
    },
    "スリーカード (3枚引き / 過去・現在・未来で、原因から今後までを占う)": {
        "num_cards": 3,
        "positions": ["過去", "現在", "未来"]
    },
    "ヘキサグラム (7枚引き / 過去・現在・未来から対策・他者・自己について占う)": {
        "num_cards": 7,
        "positions": ["過去", "現在", "未来", "対策", "周辺環境や相手", "自分について", "最終結果"]
    },
    "ソーマ法 (8枚引き / 本質や原因・問題の根源・障害・現在・近未来・未来から結果までの流れ・結果・アドバイスを読み占う)": {
        "num_cards": 8,
        "positions": ["本質・原因", "問題の根源", "障害", "現在", "近未来",
                      "近未来から結果までの流れ", "結果", "アドバイス"]
    },
    "ケルト十字 (10枚引き / 自身の現状から、障害と対策、顕在意識と潜在意識、過去と未来、本人の立ち位置と周囲の状況、願望や恐れを読み占う)": {
        "num_cards": 10,
        "positions": ["現状", "問題の障害と対策", "顕在意識", "潜在意識", "過去", "未来",
            　　　　　 "本人の立ち位置", "周囲の状況", "希望と恐れ", "最終結果"]
    },
    "ホロスコープ (13枚引き / 自身の運勢を細かく占い、今後の予想やアドバイスを提示)": {
        "num_cards": 13,
        "positions": ["自分", "金運", "勉強・知識・コミュニケーション力", "家庭・家族・プライベート",
                      "恋愛・パートナー・娯楽", "仕事・健康", "結婚・対人関係",
                      "継承・相続・性的関係", "専門分野・旅行", "評価・名誉・目的達成・天職",
                      "友人・交際・希望", "潜在意識・心理", "最終予想・アドバイス"]
    },
    "ホロスコープ・年占い (13枚引き / 占いたい年の1年を12ヶ月それぞれ占う)": {
        "num_cards": 13,
        "positions": ["1月", "2月", "3月", "4月", "5月", "6月", "7月",
                      "8月", "9月", "10月", "11月", "12月", "年間予想・アドバイス"]
    }
}

# Cloud Functionsのエントリーポイント
# POSTリクエストを受け付ける
@functions_framework.http
def tarot_fortune_api(request):

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600'
    }

    # OPTIONSリクエストへの対応
    if request.method == 'OPTIONS':
        return ('', 204, headers)

    if request.method != 'POST':
        return (jsonify({"error": "POSTリクエストのみ許可されています。"}), 405, headers)

    request_json = request.get_json(silent=True)

    if not request_json:
        return (jsonify({"error": "リクエストボディにJSONデータがありません。"}), 400, headers)

    # ユーザーからの入力
    question = request_json.get('question', '').strip()
    selected_spread_name = request_json.get('spread', '').strip()

    if not question:
        return (jsonify({"error": "占いたい内容 (question) は必須です。"}), 400, headers)
    if not selected_spread_name or selected_spread_name not in spreads:
        return (jsonify({"error": "有効な占いの方法 (spread) を指定してください。"}), 400, headers)

    selected_spread = spreads[selected_spread_name]
    num_cards_to_draw = selected_spread["num_cards"]

　　# tarot_cards.jsonの読み込みに失敗した場合
    if not tarot_cards:
        return (jsonify({"error": "タロットカードデータが読み込めませんでした。管理者にお問い合わせください。"}), 500, headers)

    drawn_cards_data = []
    try:
        drawn_card_pool = random.sample(tarot_cards, num_cards_to_draw)
    except ValueError:
        return (jsonify({"error": f"タロットカードの数が不足しています。現在のカード数: {len(tarot_cards)}、必要なカード数: {num_cards_to_draw}"}), 500, headers)


    for idx, card in enumerate(drawn_card_pool):
        is_reversed = random.choice([True, False]) # 正逆位置はランダム
        card_name = card['name']

        if is_reversed:
            meaning_short = card.get("reversed_short", "意味が見つかりません。")
            meaning_detail = card.get("reversed_detail", "意味が見つかりません。")
            position_text = '（逆位置）'
        else:
            meaning_short = card.get("upright_short", "意味が見つかりません。")
            meaning_detail = card.get("upright_detail", "意味が見つかりません。")
            position_text = '（正位置）'

        drawn_cards_data.append({
            "index": idx + 1,
            "position_name": selected_spread['positions'][idx],
            "name": card_name,
            "is_reversed": is_reversed,
            "meaning_short": meaning_short,
            "meaning_detail": meaning_detail
        })

    # geminiへのプロンプト作成
    messages = [
        {"role": "user", "parts": [
            {"text": """あなたはタロット占いの専門家であり、ユーザーの悩みに寄り添い、カードの意味に基づいて的確なアドバイスを提供するAIです。"""},
            {"text": f"""私は「{question}」という悩みについて、{selected_spread_name}というスプレッドでタロット占いをしています。"""},
            {"text": """以下のカードが引かれました。これらのカードの意味（簡易的なものと詳細なもの）、スプレッドにおける位置、そして私の悩みを総合的に考慮し、具体的なアドバイスを提供してください。"""},
            {"text": """アドバイスは、ユーザーの気持ちに寄り添い、ポジティブで行動を促すような形で、簡潔にまとめてください。\n\n"""},
        ]}
    ]

    for card_data in drawn_cards_data:
        pos_status = "逆位置" if card_data["is_reversed"] else "正位置"
        messages[0]["parts"].append({"text": f"カード {card_data['index']} ({card_data['position_name']}): {card_data['name']} ({pos_status})"})
        messages[0]["parts"].append({"text": f"  簡易的な意味: {card_data['meaning_short']}"})
        messages[0]["parts"].append({"text": f"  詳細な意味: {card_data['meaning_detail']}\n"})
    messages[0]["parts"].append({"text": "\nAIタロットからのアドバイス:\n"})

    ai_advice = "AIからのアドバイスを生成できませんでした。" # デフォルト

    try:
        model = genai.GenerativeModel(model_name=GEMINI_MODEL_NAME)
        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 2000,
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        response = model.generate_content(
            messages,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        ai_advice = response.text.strip()

    except Exception as e:
        print(f"AIアドバイスの生成中にエラーが発生しました: {e}") # Cloud Functionsのログに出力
        ai_advice = f"AIアドバイスの生成中にエラーが発生しました: {e}"

    # 引かれたカードの情報も含める
    response_data = {
        "success": True,
        "drawn_cards": drawn_cards_data,
        "ai_advice": ai_advice
    }
    return (jsonify(response_data), 200, headers)