
from langchain_community.retrievers import BM25Retriever
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from configs.load_config import LoadConfig
from source.load_db import create_sub_db, create_db
from source.utils.prompt import PROMPT_CLF_PRODUCT
import dotenv
import os
import numpy as np
import re

APP_CONFIG = LoadConfig()
dotenv.load_dotenv()


def get_tool(query: str):
    prompt = PROMPT_CLF_PRODUCT.format(query=query)
    llm = APP_CONFIG.load_chatchit_model()
    output = llm.invoke(prompt).content
    pattern = r'-?\d+(?:\.\d+)?'
    numbers = re.findall(pattern, output)
    return [int(num) for num in numbers]


def init_retriever(vector_db: Chroma, data_chunked: RecursiveCharacterTextSplitter | CharacterTextSplitter):
    """
    Arg: 
        vector db: vector db(Chroma) được khỏi tạo trong file create_db.py
        data_chunked: data được chunk (file từng sản phẩm hoặc file tất cả sản phẩm)
    Return:
        trả về  ensemble retriever kết hợp reranker 
    """

    # initialize the bm25 retriever
    retriever_BM25 = BM25Retriever.from_texts(data_chunked)
    retriever_BM25.k = APP_CONFIG.top_k

    retriever_vanilla = vector_db.as_retriever(search_type="similarity", 
                                                search_kwargs={"k": APP_CONFIG.top_k})
    
    retriever_mmr = vector_db.as_retriever(search_type="mmr", 
                                            search_kwargs={"k": APP_CONFIG.top_k})
    
    # initialize the ensemble retriever with 3 Retrievers
    ensemble_retriever = EnsembleRetriever(
        retrievers=[retriever_vanilla, retriever_mmr, retriever_BM25], weights=[0.3, 0.3, 0.4]
)
    # rerank with cohere
    compressor = CohereRerank(cohere_api_key=os.getenv("COHERE_API_KEY"))
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, 
        base_retriever=ensemble_retriever
    )
    return compression_retriever


def get_context(query: str):
    """
    Arg:
        query: câu hỏi của người dùng sau khi được rewrite.
    Return:
        phần context liên quan đến query cho llm
    """

    number = np.unique(get_tool(query=query))
    # print(number)
    # print(APP_CONFIG.id_2_name[number[0]])

    data_chunked, db = None, None
    if len(number) == 1 and number[0]== 0: # câu hỏi kh liên quan đến sản phẩm, cho llm tự trả lời
        return ""
    elif len(number) > 1 : # 2 sản phẩm trở lên, retrieval vào tất cả sản phẩm
        data_chunked, db = create_db()
    else: # truy cập vào vectordb của từng sản phẩm
        vector_db_name = APP_CONFIG.id_2_name[number[0]]
        data_chunked, db = create_sub_db(vector_db_name)

    retriever = init_retriever(vector_db=db, data_chunked=data_chunked)
    print(retriever)
    contents = retriever.invoke(input=query)

    final_content = ""
    for content in contents:
        if content.metadata['relevance_score'] > 0.7:
            final_content = final_content + content.page_content + "\n\n"
    return final_content