import gradio as gr
import openai
import json
from typing import Dict, Any, Tuple

# Load BLUF tags from JSON
def load_bluf_tags():
    bluf_tags = [
        {
            "prefix": "ACTION:",
            "example": "ACTION: Submit Timesheets by Friday",
            "description": "Recipient must take an action."
        },
        {
            "prefix": "SIGN:",
            "example": "SIGN: Approval Needed on Contract Addendum",
            "description": "Recipient needs to sign a document."
        },
        {
            "prefix": "INFO:",
            "example": "INFO: New Parking Policy Effective October 1",
            "description": "Informational only; no action required."
        },
        {
            "prefix": "DECISION:",
            "example": "DECISION: Choose Office Supply Vendor by Friday",
            "description": "Recipient must make a decision."
        },
        {
            "prefix": "REQUEST:",
            "example": "REQUEST: Vacation Days Approval for Oct 5–12",
            "description": "Sender is asking for permission or approval."
        },
        {
            "prefix": "COORD:",
            "example": "COORD: Schedule Product Launch Strategy Meeting",
            "description": "Coordination with or by the recipient is needed."
        }
    ]
    return bluf_tags

def get_system_prompt():
    return """1. **Input**:
   The user will provide the **draft body text** of an email.

2. **Output**:
   You must respond **only in JSON**. The output should always be a JSON array with a single object containing four fields:

   * `"subject"` → A concise subject line for the email. It must:
     * Begin with the most appropriate **BLUF tag** from the list below.
     * Follow with a clear subject summary.

   * `"bluf_tag"` → The BLUF tag used (e.g., `"ACTION:"`, `"INFO:"`).

   * `"bluf_summary"` → A two-sentence summary of the email, written in plain language.

   * `"email"` → The rewritten email body. It must contain:
     1. `Bottom Line Up Front` on its own line.
     2. An empty line.
     3. `Purpose: {BLUF tag}` on its own line.
     4. One empty line.
     5. The **BLUF summary**.
     6. One empty line.
     7. The **original email text** (verbatim).

3. **BLUF Tags** (choose the most fitting):

```json
[
  {
    "prefix": "ACTION:",
    "example": "ACTION: Submit Timesheets by Friday",
    "description": "Recipient must take an action."
  },
  {
    "prefix": "SIGN:",
    "example": "SIGN: Approval Needed on Contract Addendum",
    "description": "Recipient needs to sign a document."
  },
  {
    "prefix": "INFO:",
    "example": "INFO: New Parking Policy Effective October 1",
    "description": "Informational only; no action required."
  },
  {
    "prefix": "DECISION:",
    "example": "DECISION: Choose Office Supply Vendor by Friday",
    "description": "Recipient must make a decision."
  },
  {
    "prefix": "REQUEST:",
    "example": "REQUEST: Vacation Days Approval for Oct 5–12",
    "description": "Sender is asking for permission or approval."
  },
  {
    "prefix": "COORD:",
    "example": "COORD: Schedule Product Launch Strategy Meeting",
    "description": "Coordination with or by the recipient is needed."
  }
]
```

4. **Constraints**:
   * Respond **only in JSON**.
   * Never include extra commentary, markdown, or explanations outside the JSON.
   * Always return an **array** with one object."""

def format_email_with_openai(email_text: str, api_key: str) -> Tuple[str, str, str, str]:
    """Format email using OpenAI API"""
    if not api_key:
        return "❌ Error: Please provide your OpenAI API key", "", "", ""
    
    if not email_text.strip():
        return "❌ Error: Please provide email text to format", "", "", ""
    
    client = openai.OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": email_text}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse JSON response
        parsed_result = json.loads(result)
        
        if isinstance(parsed_result, list) and len(parsed_result) > 0:
            data = parsed_result[0]
        else:
            data = parsed_result
        
        subject = data.get('subject', '')
        email_body = data.get('email', '')
        bluf_tag = data.get('bluf_tag', '')
        bluf_summary = data.get('bluf_summary', '')
        
        status = "✅ Email formatted successfully!"
        
        return status, subject, email_body, f"**Tag:** {bluf_tag}\n\n{bluf_summary}"
            
    except json.JSONDecodeError as e:
        return f"❌ Error: Failed to parse AI response as JSON: {e}", "", "", ""
    except Exception as e:
        return f"❌ Error calling OpenAI API: {e}", "", "", ""

def create_bluf_reference():
    """Create BLUF tags reference text"""
    bluf_tags = load_bluf_tags()
    reference_text = "## 📚 BLUF Tags Reference\n\n"
    
    for tag in bluf_tags:
        reference_text += f"**{tag['prefix']}** - {tag['description']}\n"
        reference_text += f"*Example: {tag['example']}*\n\n"
    
    reference_text += "\n---\n\n**About BLUF:** Bottom Line Up Front (BLUF) is a communication technique that puts the most important information at the beginning of a message. It helps recipients quickly understand the purpose and required actions."
    
    return reference_text

# Create Gradio interface
def create_interface():
    """Create the main Gradio interface"""
    
    with gr.Blocks(title="📧 BLUF Email Formatter", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 📧 BLUF Email Formatter
            Transform your emails into clear, actionable communication using the **Bottom Line Up Front** methodology.
            
            **Instructions:**
            1. Enter your OpenAI API key
            2. Paste your draft email text
            3. Click "Format Email"
            4. Copy the formatted subject line and email body
            """
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 🔑 Configuration")
                api_key = gr.Textbox(
                    label="OpenAI API Key",
                    type="password",
                    placeholder="Enter your OpenAI API key...",
                    info="Your API key is not stored and only used for this session"
                )
                
                gr.Markdown("## 📝 Input")
                email_input = gr.Textbox(
                    label="Draft Email Text",
                    placeholder="Hi team, just reminding everyone that timesheets for this week are due on Friday. Please make sure to submit them by then so payroll can be processed.",
                    lines=8,
                    max_lines=15
                )
                
                format_btn = gr.Button("🚀 Format Email", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                gr.Markdown("## ✨ Formatted Output")
                
                status_output = gr.Markdown(label="Status")
                
                with gr.Group():
                    gr.Markdown("### 📬 Subject Line")
                    subject_output = gr.Textbox(
                        label="Formatted Subject",
                        interactive=False,
                        show_copy_button=True
                    )
                
                with gr.Group():
                    gr.Markdown("### 📧 Formatted Email")
                    email_output = gr.Textbox(
                        label="Formatted Email Body",
                        lines=8,
                        max_lines=15,
                        interactive=False,
                        show_copy_button=True
                    )
                
                with gr.Group():
                    gr.Markdown("### 💡 BLUF Summary")
                    summary_output = gr.Markdown()
        
        # BLUF Reference in an accordion
        with gr.Accordion("📚 BLUF Tags Reference", open=False):
            gr.Markdown(create_bluf_reference())
        
        # Set up the format button click event
        format_btn.click(
            fn=format_email_with_openai,
            inputs=[email_input, api_key],
            outputs=[status_output, subject_output, email_output, summary_output]
        )
        
        gr.Markdown(
            """
            ---
            <div style='text-align: center; color: #666;'>
            <p>Built with ❤️ using Gradio • Learn more about <a href='https://en.wikipedia.org/wiki/BLUF_(communication)' target='_blank'>BLUF Communication</a></p>
            </div>
            """
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
