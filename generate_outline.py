from pathlib import Path
from openai import OpenAI
from openai import RateLimitError
import argparse
import os
import sys
import time
 
parser = argparse.ArgumentParser()
parser.add_argument("pdf", nargs="?", default="test2.pdf")
args = parser.parse_args()
pdf_path = Path(args.pdf)
if not pdf_path.exists():
    print(f"处理失败: 未找到文件 {pdf_path}", file=sys.stderr)
    raise SystemExit(1)

client = OpenAI(
    api_key=os.getenv("MOONSHOT_API_KEY"),
    base_url = "https://api.moonshot.cn/v1",
)

file_object = client.files.create(file=pdf_path, purpose="file-extract")
 
# 获取结果
# file_content = client.files.retrieve_content(file_id=file_object.id)
# 注意，之前 retrieve_content api 在最新版本标记了 warning, 可以用下面这行代替
# 如果是旧版本，可以用 retrieve_content
file_content = client.files.content(file_id=file_object.id).text
file_content = file_content[:120000]
 
# 把它放进请求中
messages = [
    {
        "role": "system",
        "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
    },
    {
        "role": "system",
        "content": file_content,
    },
    {"role": "user", "content": "仅仅局限于文件中有的内容不要生成其他内容，其中没有的内容标记为未提供。请基于全文生成硕士论文大纲，按以下结构输出：摘要、引言、文献综述、研究方法、研究结果、讨论、结论、参考文献。要求使用分级标题（一级/二级/三级），每个一级章节下给出1-2行核心内容摘要（每行不超过50字），并尽量标注对应页码或段落位置。仅输出可直接保存为txt的大纲正文，不要解释。"},
]
 
# 然后调用 chat-completion, 获取 Kimi 的回答
def create_with_retry(max_attempts: int = 6):
    delay = 2
    for attempt in range(1, max_attempts + 1):
        try:
            return client.chat.completions.create(
                model="kimi-k2-0905-preview",
                messages=messages,
                temperature=0.3,
            )
        except RateLimitError:
            if attempt == max_attempts:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 30)

try:
    completion = create_with_retry()
    outline_text = completion.choices[0].message.content or ""
    Path("outline.txt").write_text(outline_text, encoding="utf-8")
    print("outline.txt 已生成")
except Exception as e:
    print(f"处理失败: {e}", file=sys.stderr)
    raise SystemExit(1)