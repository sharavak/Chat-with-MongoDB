import streamlit as st
from langchain.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_groq import ChatGroq
import bson
import time
from db import *
from bson import ObjectId


st.set_page_config(page_title='Chat with MongoDB Agent',page_icon='https://i.ibb.co/BLnM2NH/download.jpg',initial_sidebar_state="expanded",layout='wide')
st.sidebar.image("https://cdn-icons-png.freepik.com/64/17115/17115944.png")
st.sidebar.title("Chat with MongoDB")
st.sidebar.subheader("Just paste the MongoDB URI and chat!!!",divider=True)

def make_serializable(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    return obj

@tool
def run_pymongo_command(code_str: str) -> str | list | dict | int:
    """
    Executes a PyMongo command on a specified collection.
    Supports db['collection'].find(...) and db['collection'].aggregate(...)
    Automatically limits .find() queries to 5 results if no limit is set.
    """
    try:
        db_name = st.session_state.get("db_name", "test")
        safe_code = code_str.replace("db", f"client['{db_name}']")
        safe_globals = {"client": client}

        result = eval(safe_code, safe_globals)

        if hasattr(result, "__iter__") and not isinstance(result, (str, dict, list)):
            result = list(result)
        return make_serializable(result)

    except Exception as e:
        print("Execution Error:", e)
        return f"Execution Error: {e}"


if 'mongo_client' not in st.session_state:
    st.session_state.mongo_client=''
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
    return schema
                    

def response_generator(response):   
    for word in response:
        yield word
        time.sleep(0.01)
    
c1=st.sidebar.columns(1)    
    
with c1[0]:
    url=st.text_input(placeholder='Enter your MongoDB URI',label='MongoDB URI')
    if url:
        try:
            client=get_client(url)
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
                        with st.spinner("Fetching collections...", show_time=True):
                            st.session_state['schemas'][j]=get_schema(coll_name,j,lis_cols)
                            
                    

tools = [run_pymongo_command]
model = ChatGroq(model="llama3-70b-8192", api_key=st.secrets["API_KEY"])
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", st.secrets['temp']),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ]
)

agent = create_tool_calling_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,return_intermediate_steps=True)

msgs = StreamlitChatMessageHistory(key="chat_history")
agent_with_memory = RunnableWithMessageHistory(
    agent_executor,
    lambda session_id: msgs,
    input_messages_key="input",
    history_messages_key="history"
)

if not msgs.messages:
    msgs.add_ai_message("Hi! I am MongoDB bot.How can I assist you today?")

for msg in msgs.messages:
    role = "user" if msg.type == "human" else "assistant"
    st.chat_message(role).write(msg.content)

if prompt_text := st.chat_input("Ask MongoDB..."):
    st.chat_message("user").write(prompt_text)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("💭 _Thinking..._")
        response = agent_with_memory.invoke(
        {
            "input": prompt_text,
            "db_name": st.session_state["db_name"],
            "schemas": st.session_state["schemas"]
        },
        config={"configurable": {"session_id": "1"}},
    )
        output = response["output"]
        placeholder.empty()
        placeholder.write(response_generator(output))



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
        /*header[data-testid="stHeader"] {
            display: none;
        }*/
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