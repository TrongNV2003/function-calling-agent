import time
import streamlit as st
from agents.service.pipeline import AgentPipeline

ppl = AgentPipeline()

st.set_page_config(
    page_title="Agento",
    page_icon="🧊",
    # layout="wide",
    initial_sidebar_state="auto",
)

# Custom CSS
st.markdown("""
    <style>
        .chat-container {
            max-width: 1000px;
            margin: 0 auto;
        }
        .user-message, .bot-message {
            border-radius: 1.5rem;
            padding: .625rem 1.25rem;
            margin: 5px 0;
            display: inline-block;
            max-width: 80%;
        }
        .user-message {
            background-color: rgba(50, 50, 50, .85);
            text-align: right;
            color: white;
            font-size: 18px;
            align-self: flex-end;
        }
        .bot-message {
            background-color: transparent;
            color: white;
            font-size: 18px;
            align-self: flex-start;
        }
        .thinking-step {
            background-color: rgba(80, 80, 80, 0.5);
            padding: 10px;
            border-radius: 1.5rem;
            margin: 5px 0;
            opacity: 0.7;
            max-width: 70%;
        }
        .action-step {
            background-color: rgba(0, 100, 0, 0.5);
            padding: 10px;
            border-radius: 1.5rem;
            margin: 5px 0;
            opacity: 0.7;
            max-width: 70%;
        }
        .execution-step {
            background-color: rgba(0, 0, 100, 0.5);
            padding: 10px;
            border-radius: 1.5rem;
            margin: 5px 0;
            opacity: 0.7;
            max-width: 70%;
        }
        .final-answer {
            background-color: rgba(50, 50, 50, .85);
            padding: 10px;
            border-radius: 1.5rem;
            margin: 5px 0;
            max-width: 70%;
        }
        .error-step {
            background-color: rgba(255, 0, 0, 0.5);
            padding: 10px;
            border-radius: 1.5rem;
            margin: 5px 0;
            max-width: 70%;
        }
        .chat {
            display: flex;
            flex-direction: column;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("# :rainbow[Agento v1]")
st.sidebar.header("Agent")
selected_bot = st.sidebar.selectbox("Select chatbot:", 
                                    options=["Chatbot Basic", "Chatbot RAG"],
                                    label_visibility="collapsed")

st.sidebar.subheader("Show prompt in response")
show_prompt = st.sidebar.selectbox("Visualize prompt:", 
                                    options=["True", "False"],
                                    label_visibility="collapsed") == "True"


def query_processing(query_text, container):
    steps = []
    final_answer = ""

    def display_step(step):
        nonlocal final_answer
        steps.append(step)

        if step["type"] == "final_answer":
            final_answer = step["content"]

        html_content = ""
        for s in steps:
            if s["type"] == "thinking":
                html_content += f'<div class="thinking-step">Bước {s["step"]}: Suy nghĩ - {s["content"]}</div>'
            elif s["type"] == "action":
                html_content += f'<div class="action-step">Bước {s["step"]}: Hành động - {s["content"]}</div>'
            elif s["type"] == "execution":
                html_content += f'<div class="execution-step">Bước {s["step"]}: Thực thi - {s["content"]}</div>'
            # elif s["type"] == "final_answer":
            #     html_content += f'<div class="final-answer">Kết quả cuối cùng: {s["content"]}</div>'
            elif s["type"] == "error":
                html_content += f'<div class="error-step">Lỗi: {s["content"]}</div>'

        container.markdown(html_content, unsafe_allow_html=True)

        time.sleep(0.5)

    with st.spinner("Đang xử lý..."):
        ppl.run(query_text, step_callback=display_step, show_prompt=show_prompt)

    return final_answer

def main():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        initial_bot_message = "Hello! I am Agento. How can I assist you today?"
        st.session_state.chat_history.append({"role": "assistant", "content": initial_bot_message})

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f'<div class="chat"><div class="user-message">{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat"><div class="bot-message">{message["content"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    query_text = st.chat_input("Ask Agento something...")
    if query_text:
        st.session_state.chat_history.append({"role": "user", "content": query_text})
        st.markdown(f'<div class="chat-container"><div class="chat"><div class="user-message">{query_text}</div></div></div>', unsafe_allow_html=True)
        
        response_container = st.empty()
        
        final_answer = query_processing(query_text, response_container)

        if final_answer:
            st.session_state.chat_history.append({"role": "assistant", "content": final_answer})
            st.markdown(
                f'<div class="chat-container"><div class="chat"><div class="bot-message">{final_answer}</div></div></div>',
                unsafe_allow_html=True
            )


def health_check():
    st.sidebar.markdown("---")
    st.sidebar.header("Health Check")
    if st.sidebar.button("Kiểm tra trạng thái"):
        st.sidebar.write("I am fine! 👍🏻")

if __name__ == "__main__":
    main()
    
    health_check()
    

# streamlit run streamlit_app.py
# python -m streamlit run interface/gui.py