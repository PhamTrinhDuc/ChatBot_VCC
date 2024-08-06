import os
from dotenv import load_dotenv
import yaml
import shutil
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI


load_dotenv()
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

class LoadConfig:
    def __init__(self) -> None:
        with open("./configs/config.yml") as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)
        
        self.load_directories(app_config=app_config)
        self.load_llm_config(app_config=app_config)
        self.load_chunk_config(app_config=app_config)
        self.load_retriver_config(app_config=app_config)
        self.load_config_product(app_config=app_config)

    def load_directories(self, app_config):
        # Load parameters directories from load_config.yml file 
        self.persist_vector_directory = (
            app_config['directories']['persist_vector_directory']
        )
        self.csv_product_directory = (
            app_config['directories']['csv_product_directory']
        )
        self.text_product_directory = (
            app_config['directories']['text_product_directory']
        )

        
    def load_llm_config(self, app_config):
        # Load parameters llm from load_config.yml file 
        self.rag_model = app_config['llm_config']['rag_model']
        self.chatchit_model = app_config['llm_config']['chatchit_model']
        self.temperature = app_config['llm_config']['temperature']
        self.max_token = app_config['llm_config']['max_token']
        
    def load_retriver_config(self, app_config):
        self.vector_embed_size = app_config['retriever_config']['vector_embed_size']
        self.similarity_score = app_config['retriever_config']['similarity_score']
        self.embedding_model = app_config['retriever_config']['embedding_model']
        self.top_k = app_config['retriever_config']['top_k']
        self.score_thres = app_config['retriever_config']['score_thres']

    def load_chunk_config(self, app_config):
        self.chunk_size = app_config['chunk_config']['chunk_size']
        self.chunk_overlap = app_config['chunk_config']['chunk_overlap']

    def load_config_product(self, app_config):
        self.id_2_name = app_config['product']['id_2_name']

    def load_embedding_model(self) -> FastEmbedEmbeddings:
        embedding_model = FastEmbedEmbeddings(model_name=self.embedding_model,)
                                            #   model_kwargs = {"device":"cpu"})
        return embedding_model

    def load_rag_model(self) -> ChatGroq:
        """
        Load GROQ model using API
        """
        rag_model = ChatGroq(
                model=self.rag_model,
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=self.temperature,
                max_tokens=self.max_token,
                verbose=True,
            )
        return rag_model
    
    def load_chatchit_model(self) -> ChatGroq:
        chatchit_model = ChatGroq(
            model=self.chatchit_model,
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=self.temperature,
                max_tokens=self.max_token,
                verbose=True,
            )
        return chatchit_model
    
    def load_openai_model(self) -> ChatOpenAI:
        langchain_openai = ChatOpenAI(
            model='gpt-4o-mini',
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=self.temperature,
            max_tokens=self.max_token,
            verbose=True,
        )
        return langchain_openai

    def remove_directory(self, directory_path: str): 
        """
        Removes the specified directory.
        Parameters:
            directory_path (str): The path of the directory to be removed.
        Raises:
            OSError: If an error occurs during the directory removal process.
        Returns:
            None
        """

        if os.path.exists(directory_path):
            try:
                shutil.rmtree(directory_path)
                print(
                    f"The directory '{directory_path}' has been successfully removed.")
            except OSError as e:
                print(f"Error: {e})")
        else:
            print(f"The directory '{directory_path}' does not exist.")  
