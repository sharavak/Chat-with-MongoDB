import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq
import json, re, ast,json5,bson,time
from bson import ObjectId
from db import get_client,get_coll
from streamlit_extras.bottom_container import bottom
from mongo_query_parser import *

st.set_page_config(page_title='Chat with MongoDB',page_icon='https://i.ibb.co/BLnM2NH/download.jpg',initial_sidebar_state="expanded",layout='wide')
st.sidebar.image("https://cdn-icons-png.freepik.com/64/17115/17115944.png")
st.sidebar.title("Chat with MongoDB")
st.sidebar.subheader("Just paste the MongoDB URI and chat!!!",divider=True)


if 'schemas' not in st.session_state:
    st.session_state.schemas={}
if 'db_name' not in st.session_state:
    st.session_state['db_name']=''
if 'queries' not in st.session_state:
    st.session_state.queries=''
if 'res' not in st.session_state:
    st.session_state.res=''
if 'query' not in st.session_state:
    st.session_state.query=''
if 'cont' not in st.session_state:
    st.session_state.cont=''



def get_schema(documents,coll_name,collection_lis):
    schema={}
    for i in documents:
        for key,val  in i.items():
            if key not in schema:
                schema[key]=bson._ELEMENT_GETTER[bson.BSON.encode({"t":val})[4]].__name__[5:]
            if isinstance(val,list) and val:
                if isinstance(val[0],dict):
                    schema[key]={" type":"array",
                                    "items":{
                                    "type":"object",
                                    "properties":get_schema(val,coll_name,collection_lis)}}
                
            if isinstance(val,ObjectId):
                coll_names=collection_lis
                for col in coll_names:
                    if col==coll_name:continue
                    res=collections[col].find_one({"_id":val})
                    if res:
                        schema[key]={'type':"oid",'reference':col}
                        break
    st.session_state['schemas'][coll_name]=schema
                    

def response_generator(response):   
    for word in response:
        yield word
        time.sleep(0.01)
    
c1=st.sidebar.columns(1)    
    
with c1[0]:
    val=st.text_input(placeholder='Enter your MongoDB URI',label='MongoDB URI')
    if val:
        try:
            client=get_client(val)
            st.session_state.mongo_client=client
            client.admin.command('ping')
        except:
            st.error("Error in connecting the Database")
            st.stop()
        with c1[0]:
            dbs=client.list_database_names()
            db_option = st.selectbox(
                "Select your Database",
                dbs,
                index=None,
                placeholder="Select your Database...",
            )

        with c1[0]:
            if db_option:
                st.session_state.db_name=db_option
                collections=client[db_option]
                lis_cols=collections.list_collection_names()
                option = st.multiselect(
                    "Select your Collection name",
                    lis_cols,
                    placeholder="Select your Collection name..."
                ,key='985')
                if option:
                    for j in option:
                        coll_name=get_coll(collections,j)
                        get_schema(coll_name,j,lis_cols)
api_key=st.secrets['API_KEY']
msgs = StreamlitChatMessageHistory(key="hist")
prompt = ChatPromptTemplate.from_messages(
    [
        ("system",st.secrets['temp']+  """The schema is {schema} and database name is {db_name}"""),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | ChatGroq(model="llama3-8b-8192",api_key=api_key)
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,
    input_messages_key="question",
    history_messages_key="history",
)

tab1, tab2 = st.tabs(["💬 Chat", "🧪 Run Query"])
with tab1:
    chat_container = st.container(height=500,border=False)
    if not msgs.messages:
        msgs.add_ai_message("Hi! I am MongoDB bot.How can I assist you today?")

    for msg in msgs.messages:
        if msg.type=='human':
            chat_container.chat_message(msg.type,avatar='🧑').write(msg.content.split(".")[0])
        else:
            chat_container.chat_message(msg.type,avatar='🤖').write(msg.content)
    chat_container.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
    with bottom():
        if prompt := st.chat_input():
            chat_container.chat_message('human',avatar='🧑').write(prompt)    
            config = {"configurable": {"session_id": "1"}}
            with chat_container.chat_message("ai", avatar='🤖'):
                message_cont = st.empty()
                message_cont.markdown("_Thinking..._")
                response = chain_with_history.invoke(
                    {"question": f'{prompt}.', 'schema': f'{st.session_state["schemas"]}','db_name':f'{st.session_state["db_name"]}'},
                    config
                )
                st.session_state.cont=response.content
                message_cont.write(response_generator(response.content))
                queries=extract_mongo_queries(response.content)
                st.session_state.queries=queries


with tab2:
    if st.session_state['db_name']:
        st.markdown("### 🧪 Run MongoDB Query")
        query = st.text_area("Paste your MongoDB query (e.g., db.users.find({}))")
        sub=st.button("▶ Run")
        st.session_state.query=query
        if sub and st.session_state.query and st.session_state['db_name']:
            res = run_mongo_query(st.session_state.query)
            st.session_state.res=res
        if 'res' in st.session_state and st.session_state['db_name'] and st.session_state['res']:
            st.subheader("🔎 Query Result:")
            st.json(st.session_state.res,expanded=False)
    else:
        st.markdown("Connect your MongoDB to run the query!!!")
       

st.markdown("""
    <style>
        div[data-testid="stBottomBlockContainer"] {
             background: linear-gradient(to right, #e0c3ff, #bad1f7);
        }
        section[data-testid="stAppViewContainer"],
        section[data-testid="stAppScrollToBottomContainer"],
        body {
            background: linear-gradient(to right, #e0c3ff, #bad1f7);
        }
        header[data-testid="stHeader"] {
            display: none;
        }
        .st-emotion-cache-1gv3huu {
            box-shadow: 1px 0px 10px 0px black;
            background-color: rgb(28 77 91);
            width: 200px;
        }
        .st-emotion-cache-sy3z20 {
            color: white;
        }
    </style>
""", unsafe_allow_html=True)