import os
import gradio as gr
from database import store_data_with_vectors, ask_mixtral, register_complaint, check_complaint_status
from file_processing import handle_upload

with gr.Blocks() as demo:
    gr.Markdown("# Unified Chatbot (English Only)")
    
    with gr.Tab("Upload & Store"):
        file_input = gr.File(
            label="Upload PDF, Excel, or Image",
            file_types=[".pdf", ".xlsx", ".xls", ".png", ".jpg", ".jpeg", ".bmp"], 
            type="filepath"
        )
        upload_status = gr.Textbox(label="Status")
        upload_button = gr.Button("Upload & Embed")
        upload_button.click(fn=handle_upload, inputs=file_input, outputs=upload_status)
    
    with gr.Tab("Ask from Document"):
        user_q = gr.Textbox(label="Your Question", lines=2)
        answer = gr.Textbox(label="Answer", lines=5)
        ask_btn = gr.Button("Ask")
        ask_btn.click(fn=ask_mixtral, inputs=user_q, outputs=answer)
    
    with gr.Tab("Register Complaint"):
        name = gr.Textbox(label="Name")
        email = gr.Textbox(label="Email")
        complaint = gr.Textbox(label="Complaint", lines=4)
        register_btn = gr.Button("Submit Complaint")
        complaint_response = gr.Textbox(label="Response", lines=2)
        register_btn.click(fn=register_complaint, inputs=[name, email, complaint], outputs=complaint_response)
    
    with gr.Tab("Check Complaint Status"):
        token = gr.Textbox(label="Token")
        status = gr.Textbox(label="Complaint Status", lines=3)
        check_btn = gr.Button("Check")
        check_btn.click(fn=check_complaint_status, inputs=token, outputs=status)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)