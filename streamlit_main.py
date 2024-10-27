import streamlit as st

st.set_page_config(page_title="Home", layout="centered",page_icon='https://i.ibb.co/BLnM2NH/download.jpg')

st.markdown(
    """
    <style>
    .stMain{
        background: linear-gradient(to right, #e0c3ff, #bad1f7);
        color: white;
        font-family: Arial, sans-serif;
    }
    header[data-testid="stHeader"]{
         display:none;
    }
    h1 {
        font-size: 2rem;
        color: green;
        text-align: center;
        margin-top: 0.3em;
        font-weight: bold;
    }
    button[data-testid="stBaseButton-secondary"]{
        background-color:black;
    }
    .animated-icon {
        
        margin: 1em auto;
        display: block;
        animation: bounce 2s infinite;
    }
    .desc-box {
        border-radius: 15px;
        padding: 20px;
        font-size: 1.2em;
        color: black;
        margin: 0 auto;
        width: 70%;
        text-align: center;
    }
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-15px);
        }
        60% {
            transform: translateY(-7px);
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Welcome to Chat with MongoDB")


st.markdown("<img src='https://cdn-icons-png.freepik.com/64/1383/1383395.png' class='animated-icon'>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="desc-box">
        Simply paste the MongoDB URI and chat with bot!.
    </div>
    """,
    unsafe_allow_html=True
)

if st.button("Chat"):
    st.switch_page("pages/chat.py")