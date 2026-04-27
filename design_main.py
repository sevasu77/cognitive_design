import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import time

# --- Gemini Configuration ---
# GitHub Safety: Using st.secrets to manage the API Key.
# Ensure you have .streamlit/secrets.toml for local development.
if "API_KEY" in st.secrets:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview')
else:
    st.error("Please set your Gemini API Key in '.streamlit/secrets.toml'.")
    st.info("Template: API_KEY = 'YOUR_ACTUAL_KEY_HERE'")
    st.stop()

st.set_page_config(layout="wide", page_title="THINK ENGINE - Auto Navigation")

# --- Session State ---
if "ai_reply" not in st.session_state:
    st.session_state.ai_reply = "Waiting for cognitive seed..."
if "target_pos" not in st.session_state:
    st.session_state.target_pos = {"x": 0, "y": 0}
if "current_node" not in st.session_state:
    st.session_state.current_node = "IDLE"

# --- CSS ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #000; border-right: 1px solid #00ffcc33; }
    .stTextArea textarea { background-color: #050505; color: #00ffcc; border: 1px solid #00ffcc; }
    .stButton button { width:100%; background:transparent; color:#00ffcc; border:1px solid #00ffcc; }
</style>
""", unsafe_allow_html=True)

# --- Node Data Definitions ---
NODE_DATA = {
    "Analytical": {"x": 250, "y": -200, "prompt": "Deconstruct and analyze logically."},
    "Structured": {"x": -250, "y": -200, "prompt": "Summarize and organize into a clear structure."},
    "Realistic": {"x": -250, "y": 150, "prompt": "Calculate realistic risks and costs."},
    "Positive": {"x": 250, "y": 150, "prompt": "Reframe everything through a positive lens."}
}

# --- Sidebar (Input) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ffcc;'>SEED THOUGHT</h2>", unsafe_allow_html=True)
    user_input = st.text_area("Input thought core:", height=150, placeholder="e.g., Symbiosis between AI and Humans")
    
    if st.button("🚀 INJECT & ANALYZE"):
        if user_input:
            with st.spinner("AI measuring cognitive vectors..."):
                judge_prompt = f"For the input '{user_input}', choose the most appropriate cognitive mode from the following 4 options and reply with only one word: Analytical, Structured, Realistic, Positive"
                mode_result = model.generate_content(judge_prompt).text.strip()
                
                target_node = mode_result if mode_result in NODE_DATA else "Analytical"
                
                st.session_state.target_pos = NODE_DATA[target_node]
                st.session_state.current_node = target_node
                
                final_prompt = f"【Mode: {target_node}】\nInstruction: {NODE_DATA[target_node]['prompt']}\nSubject: {user_input}\nOutput at high density in English."
                response = model.generate_content(final_prompt)
                st.session_state.ai_reply = response.text
                st.rerun()

# --- Main Engine (HTML/JS) ---
def render_engine():
    tx = st.session_state.target_pos["x"]
    ty = st.session_state.target_pos["y"]
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; background: black; color: #00ffcc; font-family: monospace; overflow: hidden; }}
            canvas {{ display: block; }}
            #node-display {{ position: absolute; top: 10px; right: 10px; font-size: 20px; color: #00ffcc; text-shadow: 0 0 10px #00ffcc; }}
        </style>
    </head>
    <body>
        <div id="node-display">DETECTED MODE: {st.session_state.current_node}</div>
        <canvas id="c"></canvas>
        <script>
            const canvas = document.getElementById("c");
            const ctx = canvas.getContext("2d");
            let cw = canvas.width = window.innerWidth;
            let ch = canvas.height = window.innerHeight;

            let cowX = 0, cowY = 0;
            let targetX = {tx};
            let targetY = {ty};

            const nodes = [
                {{ id: "Analytical", x: 250, y: -200, color: "#00f2ff" }},
                {{ id: "Structured", x: -250, y: -200, color: "#00ff88" }},
                {{ id: "Realistic", x: -250, y: 150, color: "#ffaa00" }},
                {{ id: "Positive", x: 250, y: 150, color: "#ff007f" }}
            ];

            function draw() {{
                ctx.fillStyle = "rgba(0, 0, 0, 0.2)";
                ctx.fillRect(0, 0, cw, ch);
                cowX += (targetX - cowX) * 0.05;
                cowY += (targetY - cowY) * 0.05;

                ctx.save();
                ctx.translate(cw * 0.5, ch * 0.5);
                nodes.forEach(n => {{
                    ctx.strokeStyle = n.color;
                    let d = Math.hypot(cowX - n.x, cowY - n.y);
                    ctx.lineWidth = (d < 50) ? 5 : 1;
                    ctx.strokeRect(n.x - 60, n.y - 30, 120, 60);
                    ctx.fillStyle = n.color;
                    ctx.fillText(n.id, n.x - 50, n.y + 5);
                    if (d < 150) {{
                        ctx.beginPath();
                        ctx.moveTo(n.x, n.y);
                        ctx.lineTo(cowX, cowY);
                        ctx.stroke();
                    }}
                }});
                ctx.font = "40px serif";
                ctx.fillText("🐄", cowX - 20, cowY + 15);
                ctx.restore();
                requestAnimationFrame(draw);
            }}
            draw();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=500)

render_engine()

# --- Manual Override ---
st.markdown("### 💡 Manual Override (Alternative Interpretation)")
cols = st.columns(4)
for i, n in enumerate(NODE_DATA.keys()):
    if cols[i].button(f"Analyze as {n}"):
        st.session_state.target_pos = NODE_DATA[n]
        st.session_state.current_node = n
        prompt = f"【Mode: {n}】\nInstruction: {NODE_DATA[n]['prompt']}\nSubject: {user_input}\nOutput at high density in English."
        st.session_state.ai_reply = model.generate_content(prompt).text
        st.rerun()

# --- Result Panel ---
st.markdown(f"""
<div style="background:#000; border:1px solid #00ffcc; padding:20px; color:#e0faff; box-shadow:0 0 20px #00ffcc44;">
    <div style="font-size:10px; color:#00ffcc; margin-bottom:10px;">>>> INTERNAL_COGNITION_REPORT</div>
    <div style="white-space:pre-wrap; font-size:16px; line-height:1.6;">{st.session_state.ai_reply}</div>
</div>
""", unsafe_allow_html=True)