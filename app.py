import streamlit as st
import json
from groq import Groq

st.set_page_config(page_title="What Did I Miss?", layout="wide")

st.title("What Did I Miss? 🔍")
st.write("Lightning-fast cloud AI summarization.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Explicit API key box
    api_key = st.text_input("🔑 Groq API Key", type="password", help="Get a free key at console.groq.com")
    st.divider()
    
    current_user = st.text_input("Highlight tasks for:", "Jordan")
    uploaded_file = st.file_uploader("Upload Chat (.txt)", type=["txt"])

# --- MAIN LOGIC ---
if uploaded_file is not None:
    chat_content = uploaded_file.read().decode("utf-8")
    
    if st.button("Run Cloud Analysis", type="primary", use_container_width=True):
        
        if not api_key:
            st.error("⚠️ Please enter your Groq API key in the sidebar first.")
            st.stop()

        with st.spinner("Processing via Groq cloud..."):
            prompt = f"""
            Analyze this chat log and extract the key points.
            Respond ONLY with a JSON object containing these exact keys:
            "summary" (string: 2-sentence summary)
            "decisions" (array of strings: list of decisions)
            "action_items" (array of strings: tasks)
            "deadlines" (array of strings: times mentioned)

            Chat: {chat_content}
            """
            
            try:
                client = Groq(api_key=api_key)
                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                
                data = json.loads(completion.choices[0].message.content)
                
                st.success("Analysis Complete!")
                st.subheader("📝 Executive Summary")
                st.info(data.get("summary", "No summary found."))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.subheader("✅ Decisions")
                    for d in data.get("decisions", []): st.write(f"- {d}")
                with col2:
                    st.subheader("🎯 Action Items")
                    for a in data.get("action_items", []): 
                        if current_user.lower() in a.lower():
                            st.markdown(f"**🟢 {a}**")
                        else:
                            st.write(f"- {a}")
                with col3:
                    st.subheader("⏰ Deadlines")
                    for dl in data.get("deadlines", []): st.write(f"- {dl}")
                        
            except Exception as e:
                st.error(f"System Error: {e}")
else:
    st.info("👈 Please enter your API key and upload a text file in the sidebar to begin.")