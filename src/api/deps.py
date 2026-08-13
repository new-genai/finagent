# Dependency injection module for FastAPI
# In MVP, we keep global references here after initialization in main.py

global_retriever = None
global_executor = None
global_llm = None
global_generator = None
global_db = None
global_table_loader = None

def get_hybrid_retriever():
    return global_retriever

def get_pandas_executor():
    return global_executor

def get_llm_service():
    return global_llm

def get_submission_generator():
    return global_generator

def get_db_service():
    return global_db

def get_table_loader():
    return global_table_loader
