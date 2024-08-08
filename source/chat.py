from langchain.memory import ConversationBufferWindowMemory
from source.retriever import get_context
from configs.load_config import LoadConfig
from source.utils.base_model import GradeReWrite
from source.utils.prompt import PROMPT_HISTORY, PROMPT_HEADER


APP_CFG = LoadConfig()
memory = ConversationBufferWindowMemory(memory_key="chat_history", k=3)

def get_history():
    history = memory.load_memory_variables({})
    return history['chat_history']


def rewrite_query(query: str, history: str) -> str: 
    """
    Arg:
        query: câu hỏi của người dùng
        history: lịch sử của người dùng
        Sử dụng LLM để viết lại câu hỏi của người dùng thành 1 câu mới.
    Return:
        trả về câu hỏi được viết lại.
    """
    llm_with_output = APP_CFG.load_rewrite_model().with_structured_output(GradeReWrite)
    query_rewrite = llm_with_output.invoke(PROMPT_HISTORY.format(question=query, chat_history=history)).rewrite
    return query_rewrite


# def chat_with_history(query: str, history):
#     history_conversation = get_history()
#     query_rewrite = rewrite_query(query=query, history=history_conversation)
#     context = get_context(query=query_rewrite)
#     response = None

#     if context == "":

#         template = f'''
#         Hãy trò chuyện với khách hàng một cách thân thiện và tự nhiên. 
#         Trả lời các câu hỏi, chia sẻ thông tin hữu ích, và tham gia vào các cuộc trò chuyện đa dạng về nhiều chủ đề. 
#         Thích nghi với giọng điệu và phong cách của người dùng, đồng thời duy trì tính nhất quán và lịch sự.
#         Lưu ý: Khách hàng là người việt nên bạn chỉ được sử dụng tiếng việt

#         Question: {query}

#         Answer: '''

#         prompt = template.format(query=query)
#         response = APP_CFG.load_chatchit_model().invoke(prompt).content
        
#         memory.chat_memory.add_user_message(query)
#         memory.chat_memory.add_ai_message(response)
#         history.append((query, response))

#     else:
#         prompt_final = PROMPT_HEADER.format(question=query_rewrite, context=context)

#         response = llm.invoke(prompt_final).content

#         memory.chat_memory.add_user_message(query)
#         memory.chat_memory.add_ai_message(response)

#         history.append((query, response))

#     return "", history


def chat_with_history(query: str, history):
    history_conversation = get_history()
    query_rewrite = rewrite_query(query=query, history=history_conversation)
    context = get_context(query=query_rewrite)
    print(context)
    prompt_final = PROMPT_HEADER.format(question=query_rewrite, context=context)

    response = APP_CFG.load_rag_model().invoke(prompt_final).content

    memory.chat_memory.add_user_message(query)
    memory.chat_memory.add_ai_message(response)

    history.append((query, response))

    return "", history



# response = chat_with_history(query="Tôi muốn mua điều hòa")
# print(response)