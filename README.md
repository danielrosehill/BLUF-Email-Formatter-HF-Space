# BLUF Email Formatter (HF Space Demo)

A Streamlit-based Hugging Face Space that transforms draft emails into clear, actionable communication using the **Bottom Line Up Front (BLUF)** methodology.

## Features

- **Bring Your Own Key**: Use your OpenAI API key for processing
- **Easy Copy**: One-click copying for subject lines and formatted emails
- **BLUF Tags Reference**: Built-in guide to all BLUF communication tags
- **Clean UI**: Intuitive interface with side-by-side input/output

## BLUF Tags

- **ACTION:** Recipient must take an action
- **SIGN:** Recipient needs to sign a document  
- **INFO:** Informational only; no action required
- **DECISION:** Recipient must make a decision
- **REQUEST:** Sender is asking for permission or approval
- **COORD:** Coordination with or by the recipient is needed

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
streamlit run app.py
```

## About BLUF

Bottom Line Up Front (BLUF) is a communication technique that puts the most important information at the beginning of a message. It helps recipients quickly understand the purpose and required actions.