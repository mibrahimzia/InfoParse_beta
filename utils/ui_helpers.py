import streamlit as st

def styled_container(title, content):
    return st.markdown(f"""
    <div class="card">
        <h3>{title}</h3>
        {content}
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    st.divider()
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; color: #666;">
        <p>Built with ❤️ using Python, FastAPI, and Streamlit</p>
        <p>
            <a href="https://github.com/yourusername/webtapi" target="_blank">GitHub</a> | 
            <a href="https://huggingface.co/spaces" target="_blank">Hugging Face</a> | 
            AGPL-3.0 License
        </p>
    </div>
    """, unsafe_allow_html=True)