from flask import Flask, request, render_template_string
import os

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
    
    # サロゲート領域 or BMP外
    if 0xD800 <= code <= 0xDFFF or code > 0xFFFF:
        return True

    # 機種依存・外字・異体字の代表（丸数字 + 記号 + 異体字）
    env_chars = [
        # 丸数字など
        '①','②','③','④','⑤','⑥','⑦','⑧','⑨','⑩',
        '⑪','⑫','⑬','⑭','⑮','⑯','⑰','⑱','⑲','⑳',
        # 単位や記号
        '㍉','㌔','㌢','㍍','㌘','㌧','㏄','㍑','㍗',
        '㌍','㌦','㌣','㌫','㍊','㌻','㎜','㎝','㎞','㎎','㎏',
        '㏍','㏜','℡','№','㊤','㊥','㊦','㊧','㊨',
        # 異体字・外字・JIS外漢字
        '髙','﨑','𠮷','彅','圓','國','體','神','辻','薗','靖'
    ]

    return char in env_chars

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
