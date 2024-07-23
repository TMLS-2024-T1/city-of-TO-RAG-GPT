import gradio as gr
from chain import LLMClient, build_excerpts_vector_db, run_chain

if __name__ == '__main__':

    llm_client = LLMClient()

    excerpts_vector_db = build_excerpts_vector_db()

    with gr.Blocks(title="TMLS Hackathon 2024 city-of-TO-RAG-GPT") as demo:

        def run_chain_(
            user_query: str, 
            top_k_datasets: int, 
            df_head_n: int,
            verbose: bool,
        ):
            return run_chain(
                llm_client, 
                excerpts_vector_db, 
                user_query, 
                './data', 
                top_k_datasets,
                df_head_n,
                verbose
            )

        gr.Interface(
            title='City of Toronto RAG GPT',
            fn=run_chain_, 
            inputs=[
                gr.Textbox(label="User query"),
                gr.Slider(minimum=1, maximum=10, step=1, label="Top K datasets", value=2),
                gr.Slider(minimum=1, maximum=10, step=1, label="DataFrame head N", value=3),
                gr.Checkbox(label="Debug")
            ],
            outputs="textbox", 
            allow_flagging="never"
        )

        demo.launch(share=True, server_name="0.0.0.0", server_port=8000)