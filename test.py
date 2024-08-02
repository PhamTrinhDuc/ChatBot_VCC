import gradio as gr
from source.main import chain


# Định nghĩa các câu hỏi mẫu
example_questions = [
    "tôi muốn mua điều hòa",
    "Ai là người đầu tiên đặt chân lên mặt trăng?",
    "Python được tạo ra bởi ai?"
]

# Tạo giao diện Gradio
def chatbot(message, history):
    response = chain.invoke({'question': message})
    return response['answer']

# Tạo giao diện
iface = gr.ChatInterface(
    fn=chatbot,
    examples=example_questions,
    title="Chat với AI Assistant",
    description="Hãy đặt câu hỏi, tôi sẽ cố gắng trả lời bạn!",
    theme="soft",
)

# Thêm hình ảnh vào giao diện
iface = gr.Interface(
    fn=chatbot,
    inputs=gr.Textbox(placeholder="Nhập câu hỏi của bạn ở đây..."),
    outputs="text",
    examples=example_questions,
    title="Chat với AI Assistant",
    description="Hãy đặt câu hỏi, tôi sẽ cố gắng trả lời bạn!",
    theme="soft",
    allow_flagging="never",
)

iface.launch()