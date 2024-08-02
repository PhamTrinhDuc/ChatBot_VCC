from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from configs.load_config import LoadConfig
from source.utils.prompt import PROMPT_HEADER, PROMPT_HISTORY
import dotenv
import os


APP_CONFIG = LoadConfig()
dotenv.load_dotenv()

# Initialize Embeddings
VECTOR_DB_PATH = APP_CONFIG.persist_vector_directory


class RAG:
    def __init__(self):
        self.CONDENSE_QUESTION_PROMPT, self.QA_PROMPT = self.set_custom_prompt()
        self.data_chunked = self.load_data()
        self.embedding_model = APP_CONFIG.load_embedding_model()
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
            )
        self.compression_retriever = self.init_retriever()
        self.llm = APP_CONFIG.load_groq_model()

    def load_data(self) -> RecursiveCharacterTextSplitter:
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


    def init_retriever(self):

        #initialize the chroma retriever
        if not APP_CONFIG.persist_vector_directory:
            vectordb = Chroma.from_documents(documents=self.data_chunked, 
                                             embedding=self.embedding_model,
                                             persist_directory=APP_CONFIG.persist_vector_directory)
        else:
            vectordb = Chroma(persist_directory=APP_CONFIG.persist_vector_directory, 
                              embedding_function=self.embedding_model)


        # initialize the bm25 retriever
        retriever_BM25 = BM25Retriever.from_documents(self.data_chunked)
        retriever_BM25.k = APP_CONFIG.top_k

        retriever_vanilla = vectordb.as_retriever(search_type="similarity", 
                                                  search_kwargs={"k": APP_CONFIG.top_k})
        
        retriever_mmr = vectordb.as_retriever(search_type="mmr", 
                                              search_kwargs={"k": APP_CONFIG.top_k})
        
        # initialize the ensemble retriever with 3 Retrievers
        ensemble_retriever = EnsembleRetriever(
            retrievers=[retriever_vanilla, retriever_mmr, retriever_BM25], 
            weights=[0.3, 0.3, 0.4])
        
        # rerank with cohere
        compressor = CohereRerank(cohere_api_key=os.getenv("COHERE_API_KEY"))
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, 
            base_retriever=ensemble_retriever
        )
        return compression_retriever


    def set_custom_prompt(self):
        CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(PROMPT_HISTORY)

        QA_PROMPT = PromptTemplate(template=PROMPT_HEADER, input_variables=[
                                "question", "context"])

        return CONDENSE_QUESTION_PROMPT, QA_PROMPT


    # Instantiate the Retrieval Question Answering Chain
    def get_condense_prompt_qa_chain(self):

        model = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.compression_retriever,
            memory=self.memory,
            condense_question_prompt=self.CONDENSE_QUESTION_PROMPT,
            combine_docs_chain_kwargs={"prompt": self.QA_PROMPT})
        
        return model

rag = RAG()
chain = rag.get_condense_prompt_qa_chain()