from langchain.memory import ConversationBufferMemory
from source.retriever import get_context
from configs.load_config import LoadConfig
from source.utils.prompt import PROMPT_HISTORY, PROMPT_HEADER

APP_CFG = LoadConfig()
llm = APP_CFG.load_rag_model()
memory = ConversationBufferMemory(memory_key="chat_history")

def get_history():
    history = memory.load_memory_variables({})
    return history['chat_history']

def rewrite_query(query: str, history: str) -> str: 
    query_rewrite = llm.invoke(PROMPT_HISTORY.format(question=query, chat_history=history)).content
    return query_rewrite

# def chat_with_history(query: str, history):
#     context = get_context(query=query)
#     response = None

#     if context == "":

#         template = f"""
#         Bạn là 1 chuyên gia trong lĩnh vực trò chuyện, tâm sự với khách hàng tới mua sản phẩm bên bạn. 
#         Bạn sẽ được cung cấp 1 câu hỏi của người dùng.
#         Hãy trả lời họ và làm cho họ hài lòng. Bạn sẽ được thưởng 1000$ nếu bạn làm tốt. 
#         Lưu ý: Khách hàng là người việt nên bạn chỉ được sử dụng tiếng việt

#         Question: {query}

#         Answer: """

#         prompt = template.format(query=query)
#         response = APP_CFG.load_chatchit_model().invoke(prompt).content
        
#         memory.chat_memory.add_user_message(prompt)
#         memory.chat_memory.add_ai_message(response)
#         history.append((prompt, response))

#     else:
#         history_conversation = get_history()
#         query_rewrite = rewrite_query(query=query, history=history_conversation)
#         prompt_final = PROMPT_HEADER.format(question=query_rewrite, context=context)

#         response = llm.invoke(prompt_final).content

#         memory.chat_memory.add_user_message(prompt_final)
#         memory.chat_memory.add_ai_message(response)

#         history.append((prompt_final, response))

#     return "", history

def chat_with_history(query: str, history):
    history_conversation = get_history()
    query_rewrite = rewrite_query(query=query, history=history_conversation)
    context = get_context(query=query_rewrite)
    print(context)
    prompt_final = PROMPT_HEADER.format(question=query_rewrite, context=context)

    response = llm.invoke(prompt_final).content

    memory.chat_memory.add_user_message(query)
    memory.chat_memory.add_ai_message(response)

    history.append((query, response))

    return "", history



# response = chat_with_history(query="Tôi muốn mua điều hòa")
# print(response)