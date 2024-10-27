from pymongo import MongoClient
import streamlit as st

@st.cache_resource
def get_client(uri):
    return MongoClient(uri)

@st.cache_data
def get_coll(_collections,collection):
    return list(_collections[collection].find().limit(5))