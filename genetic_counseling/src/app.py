import gradio as gr
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

from config_manager import ConfigManager
from llm_client import OllamaClient


class GeneticCounselingApp:
    def __init__(self):
        config_dir = Path(__file__).parent.parent / "config"
        self.config_manager = ConfigManager(str(config_dir))
        
        llm_config = self.config_manager.get_llm_config()
        self.llm_client = OllamaClient(base_url=llm_config["base_url"])
        
        self.chat_history = []
    
    def chat_function(self, user_message, history):
        if not user_message.strip():
            return history
        
        llm_config = self.config_manager.get_llm_config()
        system_prompt = self.config_manager.get_system_prompt()
        
        assistant_response = self.llm_client.chat(
            user_message=user_message,
            system_prompt=system_prompt,
            model_name=llm_config["model_name"],
            temperature=llm_config["temperature"],
            max_tokens=llm_config["max_tokens"],
            top_p=llm_config["top_p"]
        )
        
        history.append((user_message, assistant_response))
        return history
    
    def update_model_config(self, model_name, temperature, max_tokens, top_p):
        self.config_manager.update_llm_config(
            model_name=model_name if model_name else None,
            temperature=temperature,
            max_tokens=int(max_tokens) if max_tokens else None,
            top_p=top_p
        )
        return "設定を更新しました"
    
    def update_system_prompt(self, prompt):
        self.config_manager.update_system_prompt(prompt)
        return "システムプロンプトを更新しました"
    
    def reset_conversation(self):
        self.llm_client.reset_conversation()
        self.chat_history = []
        return []
    
    def load_preset(self, llm_preset, prompt_preset):
        self.config_manager.reload_config(
            llm_preset=llm_preset if llm_preset != "現在の設定" else None,
            prompt_preset=prompt_preset if prompt_preset != "現在の設定" else None
        )
        
        llm_config = self.config_manager.get_llm_config()
        system_prompt = self.config_manager.get_system_prompt()
        
        return (
            llm_config["model_name"],
            llm_config["temperature"],
            llm_config["max_tokens"],
            llm_config["top_p"],
            system_prompt,
            "プリセットを読み込みました"
        )
    
    def create_ui(self):
        with gr.Blocks(title="遺伝カウンセリングエージェント", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 🧬 遺伝カウンセリング教育用エージェント")
            gr.Markdown("このシステムは、遺伝カウンセリングの練習・評価を目的としたAIエージェントです。")
            
            with gr.Row():
                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(
                        label="カウンセリングセッション",
                        height=500,
                        show_copy_button=True
                    )
                    
                    with gr.Row():
                        user_input = gr.Textbox(
                            label="あなたのメッセージ（カウンセラー役）",
                            placeholder="患者さんへのメッセージを入力してください...",
                            scale=4
                        )
                        send_btn = gr.Button("送信", variant="primary", scale=1)
                    
                    reset_btn = gr.Button("会話をリセット", variant="secondary")
                
                with gr.Column(scale=1):
                    gr.Markdown("### ⚙️ 設定パネル")
                    
                    with gr.Accordion("プリセット選択", open=True):
                        llm_preset = gr.Dropdown(
                            choices=["現在の設定", "llama3", "gemma"],
                            value="現在の設定",
                            label="LLMプリセット"
                        )
                        prompt_preset = gr.Dropdown(
                            choices=["現在の設定", "default_patient", "brca_patient"],
                            value="現在の設定",
                            label="患者プロンプトプリセット"
                        )
                        load_preset_btn = gr.Button("プリセット読み込み", variant="secondary")
                    
                    with gr.Accordion("LLMモデル設定", open=False):
                        model_name = gr.Textbox(
                            label="モデル名",
                            value=self.config_manager.get_llm_config()["model_name"],
                            placeholder="例: llama3:8b, gemma:7b"
                        )
                        
                        temperature = gr.Slider(
                            label="Temperature（創造性）",
                            minimum=0.0,
                            maximum=2.0,
                            value=self.config_manager.get_llm_config()["temperature"],
                            step=0.1
                        )
                        
                        max_tokens = gr.Number(
                            label="最大トークン数",
                            value=self.config_manager.get_llm_config()["max_tokens"],
                            minimum=256,
                            maximum=4096
                        )
                        
                        top_p = gr.Slider(
                            label="Top P（多様性）",
                            minimum=0.0,
                            maximum=1.0,
                            value=self.config_manager.get_llm_config()["top_p"],
                            step=0.05
                        )
                        
                        update_model_btn = gr.Button("モデル設定を更新", variant="secondary")
                    
                    with gr.Accordion("システムプロンプト（患者の定義）", open=False):
                        system_prompt = gr.Textbox(
                            label="システムプロンプト",
                            value=self.config_manager.get_system_prompt(),
                            lines=15,
                            placeholder="患者の振る舞いを定義するプロンプトを入力...",
                            max_lines=20
                        )
                        
                        update_prompt_btn = gr.Button("プロンプトを更新", variant="secondary")
                    
                    status_box = gr.Textbox(
                        label="ステータス",
                        value="準備完了",
                        interactive=False
                    )
            
            gr.Markdown("""
            1. **プリセット選択**: 予め定義された患者ロールとLLMモデルを選択
            2. **カスタマイズ**: モデル設定やシステムプロンプトを直接編集して独自の患者を作成
            3. **カウンセリング実践**: チャットエリアで患者役のAIと対話し、カウンセリングスキルを練習
            4. **評価**: 対話の質を確認し、改善点を見つける
            
            - **LLM実行**: Ollama（ローカルLLM）
            - **設定管理**: Hydra（Config as Code）
            - **UI**: Gradio（ブラウザ完結型）
            - **環境**: Docker（完全コンテナ化）
            """)
            
            send_btn.click(
                fn=self.chat_function,
                inputs=[user_input, chatbot],
                outputs=[chatbot]
            ).then(
                lambda: "",
                outputs=[user_input]
            )
            
            user_input.submit(
                fn=self.chat_function,
                inputs=[user_input, chatbot],
                outputs=[chatbot]
            ).then(
                lambda: "",
                outputs=[user_input]
            )
            
            reset_btn.click(
                fn=self.reset_conversation,
                outputs=[chatbot]
            )
            
            update_model_btn.click(
                fn=self.update_model_config,
                inputs=[model_name, temperature, max_tokens, top_p],
                outputs=[status_box]
            )
            
            update_prompt_btn.click(
                fn=self.update_system_prompt,
                inputs=[system_prompt],
                outputs=[status_box]
            )
            
            load_preset_btn.click(
                fn=self.load_preset,
                inputs=[llm_preset, prompt_preset],
                outputs=[model_name, temperature, max_tokens, top_p, system_prompt, status_box]
            )
        
        return demo


def main():
    app = GeneticCounselingApp()
    demo = app.create_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()
