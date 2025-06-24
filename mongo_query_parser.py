import re,json5,ast,json
import streamlit as st
def extract_mongo_queries(text):
    return re.findall(r"```(?:js|javascript|mongo)?\s*([\s\S]*?)```", text)

def load_json(str):
    return json5.loads(str)

def clean_and_parse_mongo_args(raw_args: str):
    try:
        quoted = re.sub(r'([{,]\s*)(\$?[a-zA-Z_][a-zA-Z0-9_]*)(\s*):', r'\1"\2"\3:', raw_args)
        quoted = quoted.replace("'", '"')
        return json.loads(quoted)
    except json.JSONDecodeError as e:
        return {"error": f"Execution failed: {e}"}

def run_mongo_query(query_str):
    pattern=r'db\.([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)\((.*?)\)'
    match = re.search(pattern, query_str)
    if not match:
        pattern=r'db\.([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)\((.*?)\)'
        match = re.search(pattern, query_str)
        if not match:
            return {"error": "Could not parse query."}
        _,coll_name,method, args = match.groups()
        pro,filt=re.split(r',(?![^{]*\})', args, maxsplit=1)
        args=[pro,filt]
    else:
        coll_name,method, args = match.groups()
        args = args.strip()
    db_name=st.session_state['db_name']
    client=st.session_state.mongo_client
    db = client[db_name]
    coll = db[coll_name]
    
    try:
        if method in ["count", "countDocuments"]:
            filter_dict = ast.literal_eval(args) if args else {}
            return coll.count_documents(filter_dict)
        elif method == "estimatedDocumentCount":
            return coll.estimated_document_count()
        elif method == "find":
            if '$' in args:
                filter_dict=load_json(args)
                return list(coll.find(filter_dict))
            else:
                if isinstance(args,list):
                    pro,filt=args
                    pro,filt = ast.literal_eval(pro) if pro else {}, ast.literal_eval(filt) if filt else {}
                    return list(coll.find(pro,filt))
                else:
                    filter_dict = ast.literal_eval(args) if args else {}
                    return list(coll.find(filter_dict))
        elif method == "aggregate":
            pipeline = clean_and_parse_mongo_args(args)
            return list(coll.aggregate(pipeline))
        else:
            return {"error": f"Currently Supported Methods: [find,aggregate,countDocuments]"}
    except Exception as e:
        return {"error": f"Execution failed: {e}"}