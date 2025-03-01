import requests
import streamlit as st

from agents.config.yaml_loader import load_config
from agents.service.pipeline import AgentPipeline

config = load_config()
ppl = AgentPipeline()
API_URL = config["app"]["host"]

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
            max-width: 800px;
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
        .chat {
            display: flex;
            flex-direction: column;
        }
    </style>
""", unsafe_allow_html=True)

# Chatbot params
st.markdown("# :rainbow[Agento v1]")
st.sidebar.header("Agent")
selected_bot = st.sidebar.selectbox("Select chatbot:", 
                                    options=["Chatbot Basic", "Chatbot RAG"],
                                    label_visibility="collapsed")

st.sidebar.subheader("Temperature")
temperature = st.sidebar.slider(
    "Độ sáng tạo của RAG-E:", 
    min_value=0.0, max_value=1.0, value=0.0, step=0.1,
)

st.sidebar.subheader("Threshold")
threshold = st.sidebar.slider(
    "Độ giới hạn kiến thức retrieval:", 
    min_value=0.0, max_value=2.0, value=1.0, step=0.2,
)

def Chatbot_RAG():
    # Upsert PART
    st.sidebar.markdown("---")
    st.sidebar.subheader("Select document types")
    selected_document = st.sidebar.selectbox("Chọn thể loại document muốn upsert:", 
                                        options=["Văn bản", "Thơ"])
    st.sidebar.markdown("---")
    st.sidebar.subheader("Select Upsert types")
    selected_upsert = st.sidebar.selectbox("Chọn kiểu upsert:", 
                                        options=["Upsert text", "Upsert file"])
    
    if selected_upsert == "Upsert text":
        st.sidebar.subheader("Upsert text")
        input_text = st.sidebar.text_area("Enter here:", 
                                placeholder="Nhập text cần upsert...",
                                label_visibility="collapsed")

        if st.sidebar.button("Upsert text"):
            if input_text:
                with st.spinner("Đang xử lý..."):
                    response = requests.post(
                        f"{API_URL}/upsert-text",
                        json={"index_name": config["elasticsearch"]["index_name"], "text_input": input_text}
                    )
                    if response.status_code == 200:
                        st.sidebar.write("Dữ liệu đã được upsert thành công.")
                    else:
                        st.sidebar.write("Lỗi khi gọi API:", response.status_code)
            else:
                st.write("Vui lòng nhập đầy đủ thông tin.")
    elif selected_upsert == "Upsert file":
        st.sidebar.subheader("Upsert file")
        uploaded_file = st.sidebar.file_uploader("Drag file pdf here:", 
                                        type=["pdf"],
                                        label_visibility="collapsed")
        if st.sidebar.button("Upsert file"):
            with st.spinner("Đang xử lý..."):
                response = requests.post(
                    f"{API_URL}/upsert-file?doc_type={selected_document}",
                    files={"file_path": uploaded_file}
                )
                if response.status_code == 200:
                    st.sidebar.write("Dữ liệu đã được upsert từ file.")
                else:
                    st.sidebar.write("Lỗi khi gọi API:", response.status_code)

    # Delete Index PART
    st.sidebar.markdown("---")
    st.sidebar.header("Delete Index")
    index_to_delete = st.sidebar.text_input("Nhập tên index để xoá:",
                                            placeholder='text_embeddings')
    if st.sidebar.button("Xoá Index"):
        if index_to_delete:
            response = requests.delete(
                f"{API_URL}/delete-index?index_name={index_to_delete}"
            )
            if response.status_code == 200:
                st.sidebar.write("Index đã được xoá thành công.")
            else:
                st.sidebar.write("Lỗi khi gọi API:", response.status_code)
        else:
            st.sidebar.write("Vui lòng nhập tên index.")


def query_processing(query_text):
    with st.spinner("Đang xử lý..."):
        response = ppl.run(query_text)
        
    return response

def health_check():
    st.sidebar.markdown("---")
    st.sidebar.header("Health Check")
    if st.sidebar.button("Kiểm tra trạng thái"):
        st.sidebar.write("I am fine! 👍🏻")


#Sending processing
def main():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        initial_bot_message = "Hello! I am Agento. How can I assist you today?"
        st.session_state.chat_history.append({"role": "assistant", "content": initial_bot_message})
        
    query_text = st.chat_input("Ask Agento something...")
    if query_text:
        with st.spinner("Thinking..."):
            # selected_bot = st.sidebar.selectbox("Select Bot", ["Chatbot RAG", "Chatbot Text"])

            bot_response = ppl.run(query_text)
        if bot_response:
            st.session_state.chat_history.append({"role": "user", "content": query_text})
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

    # Display chat
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f'<div class="chat"><div class="user-message">{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat"><div class="bot-message">{message["content"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
    
    # Display UI selectors
    if selected_bot == "Chatbot RAG":
        Chatbot_RAG()
    
    # Health check
    health_check()
    

# streamlit run streamlit_app.py