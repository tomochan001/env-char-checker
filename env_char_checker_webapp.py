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
    <style>
        body {
            text-align: center;
            font-size: 18px;
            font-family: sans-serif;
        }
        textarea {
            font-size: 16px;
        }
        pre {
            text-align: left;
            display: inline-block;
            margin-top: 20px;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <h1>環境依存文字チェッカー</h1>
    <form method="post">
        <textarea name="input_text" rows="10" cols="60">{{ input_text }}</textarea><br><br>
        <input type="submit" value="チェック">
    </form>
    {% if result %}
    <h2>結果:</h2>
    <pre>{{ result|safe }}</pre>
    {% endif %}
</body>
</html>
"""

# 許可文字リストの読み込み（テキストファイルを用意しておく）
with open("jis_safe_char_list.txt", encoding="utf-8") as f:
    SAFE_CHAR_SET = set(f.read())

def is_env_dependent(char):
    if char in ('\n', '\r', '\t', ' '):
        return False
    return char not in SAFE_CHAR_SET

def find_problematic_lines(text):
    lines = text.splitlines()
    result_lines = []
    for lineno, line in enumerate(lines, 1):
        for char in line:
            if is_env_dependent(char):
                result_lines.append((lineno, char, f"U+{ord(char):04X}"))
    return result_lines

@app.route("/", methods=["GET", "POST"])
def index():
    input_text = ""
    result = ""
    if request.method == "POST":
        input_text = request.form["input_text"]
        problematic = find_problematic_lines(input_text)
        if problematic:
            result = "環境依存文字が見つかりました：<br><br>" + "<br>".join(
                f"<span style='color: red; font-weight: bold;'>{lineno}行目:</span> "
                f"<span style='color: navy;'>{c} ({code})</span>"
                for lineno, c, code in problematic)
        else:
            result = "環境依存文字は見つかりませんでした。"
    return render_template_string(HTML_TEMPLATE, input_text=input_text, result=result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
