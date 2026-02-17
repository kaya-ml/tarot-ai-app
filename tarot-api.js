// js/tarot-api.js
document.addEventListener('DOMContentLoaded', () => {
    const API_ENDPOINT = 'Google Cloud Functionsの公開URL';
    const tarotForm = document.getElementById('tarot-form');
    const questionInput = document.getElementById('question');
    const spreadSelect = document.getElementById('spread');
    const resultDiv = document.getElementById('tarot-result');
    const loadingDiv = document.getElementById('loading-indicator');

    if (tarotForm) {
        tarotForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // フォームのデフォルト送信を防止

            const question = questionInput.value;
            const spread = spreadSelect.value;

            if (!question || !spread) {
                alert('質問と占いの種類を入力してください。');
                return;
            }

            loadingDiv.style.display = 'block'; // ローディング表示
            resultDiv.innerHTML = ''; // 前の結果をクリア

            try {
                const response = await fetch(API_ENDPOINT, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question, spread }),
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`APIエラー: ${response.status} - ${errorData.error || '不明なエラー'}`);
                }

                const data = await response.json();
                loadingDiv.style.display = 'none'; // ローディング非表示

                if (data.success) {
                    let htmlContent = '<h3>引かれたカード</h3>';
                    data.drawn_cards.forEach(card => {
                        htmlContent += `
                            <div class="tarot-card-display">
                                <h4>${card.position_name}: ${card.name} (${card.is_reversed ? '逆位置' : '正位置'})</h4>
                                <p><strong>短い意味:</strong> ${card.meaning_short}</p>
                                <p><strong>詳細な意味:</strong> ${card.meaning_detail}</p>
                            </div>
                        `;
                    });

                    htmlContent += '<h3>AIからのアドバイス</h3>';
                    if (data.ai_advice) {
                         // Unicodeエスケープシーケンスをデコード
                        const decodedAiAdvice = data.ai_advice.replace(/\\u[\dA-F]{4}/gi, 
                            function (match) {
                                return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
                            });
                        htmlContent += `<p>${decodedAiAdvice}</p>`;
                    } else {
                        htmlContent += `<p>AIアドバイスの生成中に問題が発生しました。</p>`;
                    }

                    resultDiv.innerHTML = htmlContent;
                } else {
                    resultDiv.innerHTML = `<p style="color: red;">エラー: ${data.error || '不明なエラー'}</p>`;
                }
            } catch (error) {
                loadingDiv.style.display = 'none'; // ローディング非表示
                resultDiv.innerHTML = `<p style="color: red;">通信エラーが発生しました: ${error.message}</p>`;
                console.error('Fetch error:', error);
            }
        });
    }
});