import streamlit as st
import openai
import json
from typing import Dict, Any
import pyperclip

# Page configuration
st.set_page_config(
    page_title="BLUF Email Formatter",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load BLUF tags from JSON
@st.cache_data
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

def format_email_with_openai(email_text: str, api_key: str) -> Dict[str, Any]:
    """Format email using OpenAI API"""
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
            return parsed_result[0]
        else:
            return parsed_result
            
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse AI response as JSON: {e}")
        return None
    except Exception as e:
        st.error(f"Error calling OpenAI API: {e}")
        return None

def copy_to_clipboard_js(text: str, button_id: str):
    """Generate JavaScript for copying text to clipboard"""
    return f"""
    <script>
    function copyToClipboard_{button_id}() {{
        navigator.clipboard.writeText(`{text}`).then(function() {{
            console.log('Copied to clipboard');
        }}, function(err) {{
            console.error('Could not copy text: ', err);
        }});
    }}
    </script>
    <button onclick="copyToClipboard_{button_id}()" style="
        background-color: #ff6b6b;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        margin-left: 10px;
    ">📋 Copy</button>
    """

# Main app
def main():
    st.title("📧 BLUF Email Formatter")
    st.markdown("Transform your emails into clear, actionable communication using the **Bottom Line Up Front** methodology.")
    
    # Sidebar for API key and BLUF info
    with st.sidebar:
        st.header("🔑 Configuration")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key to use the formatter"
        )
        
        st.header("📚 BLUF Tags Reference")
        bluf_tags = load_bluf_tags()
        
        for tag in bluf_tags:
            with st.expander(f"{tag['prefix']} - {tag['description']}"):
                st.write(f"**Example:** {tag['example']}")
                st.write(f"**Use when:** {tag['description']}")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Input Email")
        email_input = st.text_area(
            "Paste your draft email text here:",
            height=300,
            placeholder="Hi team, just reminding everyone that timesheets for this week are due on Friday. Please make sure to submit them by then so payroll can be processed."
        )
        
        format_button = st.button("🚀 Format Email", type="primary", disabled=not api_key or not email_input)
    
    with col2:
        st.header("✨ Formatted Output")
        
        if format_button and api_key and email_input:
            with st.spinner("Formatting your email..."):
                result = format_email_with_openai(email_input, api_key)
                
                if result:
                    # Store result in session state
                    st.session_state.formatted_result = result
        
        # Display results if available
        if hasattr(st.session_state, 'formatted_result') and st.session_state.formatted_result:
            result = st.session_state.formatted_result
            
            # Subject line with copy button
            st.subheader("📬 Subject Line")
            subject_container = st.container()
            with subject_container:
                col_subject, col_copy_subject = st.columns([4, 1])
                with col_subject:
                    st.code(result.get('subject', ''), language=None)
                with col_copy_subject:
                    if st.button("📋", key="copy_subject", help="Copy subject line"):
                        try:
                            pyperclip.copy(result.get('subject', ''))
                            st.success("Copied!")
                        except:
                            st.info("Copy manually from above")
            
            # Formatted email with copy button
            st.subheader("📧 Formatted Email")
            email_container = st.container()
            with email_container:
                col_email, col_copy_email = st.columns([4, 1])
                with col_email:
                    st.text_area(
                        "Formatted email body:",
                        value=result.get('email', ''),
                        height=200,
                        key="formatted_email_display"
                    )
                with col_copy_email:
                    if st.button("📋", key="copy_email", help="Copy formatted email"):
                        try:
                            pyperclip.copy(result.get('email', ''))
                            st.success("Copied!")
                        except:
                            st.info("Copy manually from above")
            
            # BLUF Summary (display only)
            st.subheader("💡 BLUF Summary")
            st.info(f"**Tag:** {result.get('bluf_tag', '')}")
            st.write(result.get('bluf_summary', ''))
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        <p>Built with ❤️ using Streamlit • Learn more about <a href='https://en.wikipedia.org/wiki/BLUF_(communication)' target='_blank'>BLUF Communication</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
