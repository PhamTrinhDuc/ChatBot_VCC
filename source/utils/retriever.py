
from langchain_community.document_loaders import CSVLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from configs.load_config import LoadConfig
import dotenv
import os


APP_CONFIG = LoadConfig()
dotenv.load_dotenv()


def load_data()-> RecursiveCharacterTextSplitter:
        """
        Load file PDF using PyMuPDFLoader
        """
        DATA_PATH = APP_CONFIG.data_product_directory

        # loader = DirectoryLoader(DATA_PATH, glob="**/*.csv", 
        #                          use_multithreading=True, show_progress=True)
        # documents = loader.load()

        loader = CSVLoader(DATA_PATH)
        documents = loader.load()

        docs = RecursiveCharacterTextSplitter(
            chunk_size=APP_CONFIG.chunk_size,
            chunk_overlap=APP_CONFIG.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        ).split_documents(documents=documents)
        return docs


def init_retriever():

    data_chunked = load_data()

    #initialize the chroma retriever
    if not APP_CONFIG.persist_vector_directory:
        vectordb = Chroma.from_documents(documents=data_chunked, 
                                            embedding=APP_CONFIG.load_embedding_model(),
                                            persist_directory=APP_CONFIG.persist_vector_directory)
    else:
        vectordb = Chroma(persist_directory=APP_CONFIG.persist_vector_directory, 
                            embedding_function=APP_CONFIG.load_embedding_model())


    # initialize the bm25 retriever
    retriever_BM25 = BM25Retriever.from_documents(data_chunked)
    retriever_BM25.k = APP_CONFIG.top_k

    retriever_vanilla = vectordb.as_retriever(search_type="similarity", 
                                                search_kwargs={"k": APP_CONFIG.top_k})
    
    retriever_mmr = vectordb.as_retriever(search_type="mmr", 
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


retriever = init_retriever()