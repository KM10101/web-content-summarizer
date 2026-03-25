# Web Content Summarizer

最小可运行版本：输入 URL，抓取网页正文并输出结构化总结。

## 1) 环境变量

在项目根目录放置 `.env` 文件，至少包含：

```env
base_url=https://api.openai.com/v1
api_key=YOUR_API_KEY
model=gpt-4.1-mini
```

可选变量：

```env
request_timeout_seconds=20
max_input_chars=12000
output_dir=runs
```

## 2) 运行方式

```bash
uv run python main.py "https://example.com/article"
```

指定输出语言（默认中文）：

```bash
uv run python main.py "https://example.com/article" --language English
```

关闭落盘：

```bash
uv run python main.py "https://example.com/article" --no-save
```

## 3) 输出结构

程序会输出并校验如下结构：

```json
{
  "title": "",
  "summary": "",
  "keyPoints": [],
  "actionItems": [],
  "tags": []
}
```
