import streamlit as st
import time
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq
import bson
from bson import ObjectId
from db import get_client,get_coll

st.set_page_config(page_title='Chat with MongoDB',page_icon='https://i.ibb.co/BLnM2NH/download.jpg',initial_sidebar_state="expanded",layout='wide')
st.sidebar.image("https://cdn-icons-png.freepik.com/64/17115/17115944.png")
st.sidebar.title("Chat with MongoDB")
st.sidebar.subheader("Just paste the MongoDB URI and chat!!!",divider=True)


def get_schema(documents,coll_name,collection_lis):
    schema={}
    for i in documents:
        for key,val  in i.items():
            if key not in schema:
                schema[key]=bson._ELEMENT_GETTER[bson.BSON.encode({"t":val})[4]].__name__[5:]
            if isinstance(val,list):
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


c1=st.sidebar.columns(1)    

api_key=api_key=st.secrets['API_KEY']



msgs = StreamlitChatMessageHistory(key="hist")
    
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
                collections=client[db_option]
                lis_cols=collections.list_collection_names()
                option = st.selectbox(
                    "Select your Collection name",
                    lis_cols,
                    index=None,
                    placeholder="Select your Collection name..."
                ,key='985')
                if option:
                    if option not in st.session_state:
                        coll_name=get_coll(collections,option)
                        sch=get_schema(coll_name,option,lis_cols)
                        st.session_state[option]=sch
                    st.session_state['collection']=st.session_state.get(option)
                    msgs.add_ai_message(f"Hi, you provided {option.title()} schema. Are you looking for any query?")


def response_generator(response):    
    for word in response:
        yield word
        time.sleep(0.01)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system",st.secrets['temp']+  """The schema is {schema}"""),
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


if not msgs.messages:
    msgs.add_ai_message("Hi! I am MongoDB bot.How can I assist you today?")

for msg in msgs.messages:
    if msg.type=='human':
        st.chat_message(msg.type,avatar='🧑').write(msg.content.split(".")[0])
    else:
        st.chat_message(msg.type,avatar='🤖').write(msg.content)

if prompt := st.chat_input():
    st.chat_message('human',avatar='🧑').write(prompt)    
    config = {"configurable": {"session_id": "1"}}
    response = chain_with_history.invoke({"question": f'{prompt}.','schema':f'{st.session_state.get('collection',{})}'}, config)
    st.chat_message("ai",avatar='🤖').write(response_generator(response.content))


st.markdown("""
    <style>
        div[data-testid="stBottomBlockContainer"] {
             background: linear-gradient(to right, #e0c3ff, #bad1f7);
            }
        body {{
            background: linear-gradient(to right, #e0c3ff, #bad1f7);
            }}
        [data-testid="stAppViewContainer"]{{
            background: linear-gradient(to right, #e0c3ff, #bad1f7);
            }}
        section[data-testid="stAppScrollToBottomContainer"]{
            background: linear-gradient(to right, #e0c3ff, #bad1f7);
            color: white;
            font-family: Arial, sans-serif;
        } 
        .st-emotion-cache-1gv3huu{
                box-shadow: 1px 0px 10px 0px black;
                background-color: rgb(28 77 91);
                width: 200px;
            }
    
        .st-emotion-cache-sy3z20{
                color:white;
            }
            header[data-testid="stHeader"].ezrtsby2{
                display:none;
            }
            <\style>
            """
,unsafe_allow_html=True)