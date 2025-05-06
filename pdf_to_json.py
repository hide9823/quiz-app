import json
import re
import PyPDF2
import tkinter as tk
from tkinter import filedialog


# エクスプローラー形式のダイアログでPDFを選択する
root = tk.Tk()
root.withdraw()  # メインウィンドウは不要
pdf_path = filedialog.askopenfilename(
    title="PDFファイルを選択してください",
    filetypes=[("PDF files", "*.pdf")]
)
if not pdf_path:
    print("❌ ファイルが選択されませんでした。終了します。")
    exit(1)

# PDF を開き、全ページのテキストを抽出
reader = PyPDF2.PdfReader(pdf_path)
full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

# 「問題番号」から「禁転載複製」までを分割
pattern = r"問題(\d+)[\s\S]*?(?=問題\d+|禁転載複製)"
parts = re.split(pattern, full_text)[1:]

questions = []
for i in range(0, len(parts), 2):
    num = int(parts[i].strip())
    block = parts[i+1].strip()
    m = re.search(r"(.*?)(ア．.+)", block, re.DOTALL)
    if not m:
        continue
    q_text = m.group(1).replace("\n", " ").strip()
    choices_text = m.group(2).strip()
    choices = dict(re.findall(r"([アイウエ])．\s*([^アイウエ]+)", choices_text))
    questions.append({
        "question_number": num,
        "question_text": q_text,
        "choices": {k: v.strip().replace("\n", " ") for k, v in choices.items()}
    })

# JSON に書き出し
output_path = "operation_quiz.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"✅ JSON を生成しました: {output_path}")