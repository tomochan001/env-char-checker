from flask import Flask, request, render_template_string
import os
import unicodedata

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <title>環境依存文字チェッカー（Web版）</title>
</head>
<body>
    <h1>環境依存文字チェッカー</h1>
    <form method="post">
        <textarea name="input_text" rows="10" cols="60">{{ input_text }}</textarea><br><br>
        <input type="submit" value="チェック">
    </form>
    {% if result %}
    <h2>結果:</h2>
    <pre>{{ result }}</pre>
    {% endif %}
</body>
</html>
"""

def is_env_dependent(char):
    code = ord(char)

    # 許可：ASCII記号、カタカナ、ひらがな、基本漢字範囲（JIS第1・第2水準相当）
    if (
        0x0020 <= code <= 0x007E or   # ASCII
        0x3040 <= code <= 0x309F or   # ひらがな
        0x30A0 <= code <= 0x30FF or   # カタカナ
        0x4E00 <= code <= 0x9FFF or   # CJK統合漢字（漢字の主な範囲）
        0xFF01 <= code <= 0xFF60      # 全角記号など
    ):
        return False

    # それ以外は機種依存（メルマガ非推奨）
    return True

@app.route("/", methods=["GET", "POST"])
def index():
    input_text = ""
    result = ""
    if request.method == "POST":
        input_text = request.form["input_text"]
        problematic = [(c, f"U+{ord(c):04X}") for c in input_text if is_env_dependent(c)]
        if problematic:
            result = "環境依存文字が見つかりました：\n\n" + "\n".join(f"{c} ({code})" for c, code in problematic)
        else:
            result = "環境依存文字は見つかりませんでした。"
    return render_template_string(HTML_TEMPLATE, input_text=input_text, result=result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
