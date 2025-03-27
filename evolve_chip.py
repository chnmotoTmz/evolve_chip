import os
import threading
import time
import queue
from typing import List, Dict, Optional
from loguru import logger
from datetime import datetime
import json
import sys
import google.generativeai as genai

class EvolveChip:
    def __init__(self, app):
        self.app = app
        self.evolving = False
        self.thread: Optional[threading.Thread] = None
        self.evolution_history = []
        self._lock = threading.Lock()
        self.queue = queue.Queue()  # スレッド間通信用のキュー
        
        # 進化の方向性の設定
        self.evolution_direction = {
            "comment": ""  # ユーザーからの進化方向のコメント
        }
        
        # Gemini APIの設定
        try:
            # 環境変数からAPIキーを取得
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.error("GEMINI_API_KEY環境変数が設定されていません")
                self.model = None
                return
            
            genai.configure(api_key=api_key)
            
            # 利用可能なモデルを確認
            available_models = genai.list_models()
            model_names = [model.name for model in available_models]
            logger.info(f"利用可能なモデル: {model_names}")
            
            # 優先順位に従ってモデルを選択
            preferred_models = [
                'models/gemini-1.5-pro-002',  # 最新の安定版
                'models/gemini-1.5-pro-latest',  # 最新版
                'models/gemini-1.5-pro',  # 標準版
                'models/gemini-2.0-pro-exp'  # 実験版
            ]
            
            selected_model = None
            for model_name in preferred_models:
                if model_name in model_names:
                    selected_model = model_name
                    break
            
            if not selected_model:
                logger.error("利用可能なGeminiモデルが見つかりません")
                self.model = None
                return
            
            self.model = genai.GenerativeModel(selected_model)
            logger.info(f"Gemini APIの初期化に成功: {selected_model}")
        except Exception as e:
            logger.error(f"Gemini APIの初期化に失敗: {str(e)}")
            self.model = None
        
        logger.info("AIチップを初期化しました")
    
    def set_evolution_direction(self, direction: Dict[str, str]):
        """進化の方向性を設定します"""
        self.evolution_direction.update(direction)
        logger.info(f"進化の方向性を更新: {json.dumps(self.evolution_direction, ensure_ascii=False)}")
    
    def start_evolving(self):
        """ブログの進化を開始します"""
        if self.evolving:
            logger.warning("既に進化中です")
            return
        
        if not self.model:
            logger.error("Gemini APIが初期化されていません")
            return
        
        self.evolving = True
        self.app.disable_buttons()
        
        # 進化処理を別スレッドで実行
        self.thread = threading.Thread(target=self._evolve_process)
        self.thread.start()
    
    def _evolve_process(self):
        """ブログを進化させる処理を実行します"""
        try:
            # 現在のブログ内容を取得
            content = self.app.content_text.get('1.0', 'end').strip()
            
            # 進化の方向性に基づいてプロンプトを生成
            direction_prompt = self._generate_direction_prompt()
            
            # Gemini APIを使用してブログを進化
            prompt = f"""
            以下のブログ記事を改善してください：
            
            {content}
            
            進化の方向性：
            {direction_prompt}
            
            改善のポイント：
            1. より魅力的なタイトル
            2. 文章の流れの改善
            3. 具体例の追加
            4. 読みやすさの向上
            
            改善された記事を返してください。
            """
            
            logger.info("Gemini APIにリクエストを送信")
            response = self.model.generate_content(prompt)
            logger.info("Gemini APIからレスポンスを受信")
            
            if response.text:
                # UIを更新
                self.app.root.after(0, self._update_content, response.text)
            else:
                logger.error("Gemini APIからの応答が空でした")
        
        except Exception as e:
            logger.error(f"進化プロセス中にエラー: {str(e)}")
        finally:
            self.evolving = False
            self.app.root.after(0, self.app.enable_buttons)
    
    def _generate_direction_prompt(self) -> str:
        """進化の方向性に基づいてプロンプトを生成します"""
        if "comment" in self.evolution_direction:
            return f"""
            以下の要望に従ってブログを改善してください：
            {self.evolution_direction['comment']}
            
            改善の際は以下の点も考慮してください：
            1. 文章の流れと一貫性
            2. 読者への伝わりやすさ
            3. 具体的な例示
            4. 適切な段落構成
            """
        return "ブログの内容を改善してください。"
    
    def _update_content(self, new_content: str):
        """UIのコンテンツを更新します"""
        try:
            self.app.content_text.delete('1.0', 'end')
            self.app.content_text.insert('1.0', new_content)
            logger.info("ブログ内容を更新しました")
        except Exception as e:
            logger.error(f"コンテンツ更新中にエラー: {str(e)}")
    
    def evolve(self):
        """ブログ記事を進化させます"""
        try:
            self.app.disable_buttons()  # ボタンを無効化
            time.sleep(3)  # 模擬的な成長時間
            
            if self.evolving:
                for blog_id in self.app.blog_storage.list_blogs():
                    if not self.evolving:
                        break
                        
                    # 元のブログ記事を読み込み
                    original_content = self.app.blog_storage.load_blog(blog_id)
                    
                    # 進化提案を生成
                    evolution_suggestion = self.generate_evolution(original_content)
                    
                    # 進化を適用
                    evolved_content = self.apply_evolution(original_content, evolution_suggestion)
                    
                    # 新しい内容を保存
                    self.app.blog_storage.save_blog(blog_id, evolved_content)
                    
                    # 進化履歴を記録
                    self.record_evolution(blog_id, original_content, evolved_content, evolution_suggestion)
                    
                    # 結果をキューに送信
                    self.queue.put((blog_id, evolved_content))
                    logger.info(f"ブログを進化: {blog_id}")
            
            # 完了通知をキューに送信
            self.queue.put("COMPLETE")
            
            # 進化履歴を保存
            self.save_evolution_history()
        except Exception as e:
            logger.error(f"進化プロセスでエラー: {str(e)}")
            self.queue.put("COMPLETE")  # エラー時も完了通知
        finally:
            self.evolving = False
    
    def generate_evolution(self, content: List[str]) -> str:
        """進化提案を生成します"""
        # ここでは単純な進化提案を返します
        # 実際の実装では、より高度な進化ロジックを実装できます
        return "こんにちは、世界！今日は素晴らしい一日でした。新しい発見がありました。"
    
    def apply_evolution(self, original_content: List[str], evolution_suggestion: str) -> List[str]:
        """進化提案を適用します"""
        evolved_lines = []
        title_found = False
        
        for line in original_content:
            if line.strip().startswith("#"):
                evolved_lines.append(line)
                title_found = True
            elif title_found and line.strip():
                evolved_lines.append(evolution_suggestion)
                title_found = False
            else:
                evolved_lines.append(line)
        
        return evolved_lines
    
    def record_evolution(self, blog_id: str, original_content: List[str], 
                        evolved_content: List[str], evolution_suggestion: str):
        """進化履歴を記録します"""
        evolution_record = {
            "timestamp": datetime.now().isoformat(),
            "blog_id": blog_id,
            "original_length": len(original_content),
            "evolved_length": len(evolved_content),
            "evolution_suggestion": evolution_suggestion,
            "metadata": {
                "title": next((line for line in original_content if line.strip().startswith("#")), ""),
                "original_paragraphs": len([line for line in original_content if line.strip() and not line.strip().startswith("#")]),
                "evolved_paragraphs": len([line for line in evolved_content if line.strip() and not line.strip().startswith("#")])
            }
        }
        
        self.evolution_history.append(evolution_record)
        logger.info(f"進化履歴を記録: {json.dumps(evolution_record, ensure_ascii=False)}")
    
    def save_evolution_history(self):
        """進化履歴を保存します"""
        try:
            history_file = "evolution_history.json"
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(self.evolution_history, f, ensure_ascii=False, indent=2)
            logger.info("進化履歴を保存しました")
        except Exception as e:
            logger.error(f"進化履歴の保存に失敗: {str(e)}")
    
    def cleanup(self):
        """リソースのクリーンアップを行います"""
        try:
            self.evolving = False
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=1.0)
            logger.info("AIチップのクリーンアップが完了")
        except Exception as e:
            logger.error(f"クリーンアップ中にエラー: {str(e)}")

def main():
    """単体テスト用のメイン関数"""
    import tkinter as tk
    from tkinter import ttk, scrolledtext
    
    class MockApp:
        def __init__(self):
            self.root = tk.Tk()
            self.root.title("AIチップテスト")
            
            # 進化の方向性を設定するUI
            direction_frame = ttk.LabelFrame(self.root, text="進化の方向性")
            direction_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # スタイル選択
            ttk.Label(direction_frame, text="スタイル:").grid(row=0, column=0, padx=5, pady=2)
            style_var = tk.StringVar(value="formal")
            style_combo = ttk.Combobox(direction_frame, textvariable=style_var, 
                                     values=["formal", "casual", "technical", "creative"])
            style_combo.grid(row=0, column=1, padx=5, pady=2)
            
            # トーン選択
            ttk.Label(direction_frame, text="トーン:").grid(row=1, column=0, padx=5, pady=2)
            tone_var = tk.StringVar(value="professional")
            tone_combo = ttk.Combobox(direction_frame, textvariable=tone_var,
                                    values=["professional", "friendly", "humorous", "serious"])
            tone_combo.grid(row=1, column=1, padx=5, pady=2)
            
            self.content_text = scrolledtext.ScrolledText(self.root)
            self.content_text.pack(expand=True, fill='both', padx=5, pady=5)
            self.content_text.insert('1.0', "これはテスト用のブログ記事です。\n\nAIによって進化させることができます。")
            
            def start_evolve():
                # 進化の方向性を設定
                direction = {
                    "style": style_var.get(),
                    "tone": tone_var.get()
                }
                self.chip.set_evolution_direction(direction)
                self.chip.start_evolving()
            
            self.button = ttk.Button(self.root, text="進化", command=start_evolve)
            self.button.pack(pady=5)
            
            self.chip = EvolveChip(self)
        
        def disable_buttons(self):
            self.button["state"] = "disabled"
        
        def enable_buttons(self):
            self.button["state"] = "normal"
    
    app = MockApp()
    app.root.mainloop()

if __name__ == "__main__":
    main() 