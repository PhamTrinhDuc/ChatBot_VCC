
import streamlit as st
from source.main import chain
from source.main2 import conversational_rag_chain

# upload_file = st.file_uploader(label="Upload your file csv is here")
# df = pd.read_csv(upload_file)
# st.dataframe(df, width=1800, height=1200)

chat_history = []
st.session_state.messages = []
#Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages =[]

#Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#React to user input
if prompt := st.chat_input("Ask question to document assistant"):
    #Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    #Add user message to chat history
    st.session_state.messages.append({"role":"user","context": prompt})

    response1 = f"Echo: {prompt}"
    #Display assistant response in chat message container
    response = chain.invoke({'question':prompt,'chat_history':chat_history})
    # response = conversational_rag_chain.invoke(
    #     {"input": prompt},
    #     config={
    #         "configurable": {"session_id": "abc123"}
    #     },  # constructs a key "abc123" in `store`.
    # )["answer"]

    with st.chat_message("assistant"):
        st.markdown(response['answer'])

    st.session_state.messages.append({'role':"assistant", "content":response})
    chat_history.append({prompt,response['answer']})
