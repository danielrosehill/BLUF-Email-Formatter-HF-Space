# BLUF Email Formatter

A Gradio-based Hugging Face Space that transforms draft emails into clear, actionable communication using the **Bottom Line Up Front (BLUF)** methodology.

[Learn more about BLUF](https://hbr.org/2016/11/how-to-write-email-with-military-precision).

## Features

- **Bring Your Own Key**: Use your OpenAI API key for processing
- **Easy Copy**: One-click copying for subject lines and formatted emails
- **BLUF Tags Reference**: Built-in guide to all BLUF communication tags
- **Clean UI**: Intuitive interface with side-by-side input/output

## BLUF Tags

- **ACTION:** Requests action from recipient
- **SIGN:** Signature request from recipient
- **INFO:** Informational only; no action required
- **DECISION:** Requests decision from recipient
- **REQUEST:** Request/approval
- **COORD:** Information shared for visibility and coordination among team

## How It Works

1. Enter your OpenAI API key in the sidebar
2. Paste your draft email text
3. Click "Format Email" 
4. Copy the formatted subject line and email body
5. Use the BLUF summary for reference

## Output Format

UI generates:

- **Subject Line**: BLUF tag + concise summary
- **Formatted Email**: Structured with BLUF methodology
- **BLUF Summary**: Two-sentence plain language summary

## 🔧 Local Development

```bash
pip install -r requirements.txt
python app.py
```

## About BLUF

Bottom Line Up Front (BLUF) is a communication technique that puts the most important information at the beginning of a message. It helps recipients quickly understand the purpose and required actions.