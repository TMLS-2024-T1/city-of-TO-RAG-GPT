import gradio as gr
from eval import query_to_answer


with gr.Blocks(title="TMLS Hackathon 2024") as demo:
    gr.Interface(fn=query_to_answer, inputs="textbox", outputs="textbox", allow_flagging="never")
    demo.launch(share=True, server_name="0.0.0.0", server_port=8000)


