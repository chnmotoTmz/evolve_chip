import os
import threading
import time
import queue
from typing import List, Dict, Optional, Callable, Any
from loguru import logger
from datetime import datetime
import json
import sys
import google.generativeai as genai

class EvolveChip:
    """AIチップの基本クラス"""
    def __init__(self, host_system):
        self.host = host_system
        self.model = None
        self._setup_gemini()
    
    def _setup_gemini(self):
        """Gemini APIの初期化"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.error("GEMINI_API_KEY環境変数が設定されていません")
                return None
            
            genai.configure(api_key=api_key)
            available_models = genai.list_models()
            model_names = [model.name for model in available_models]
            
            preferred_models = [
                'models/gemini-1.5-pro-002',
                'models/gemini-1.5-pro-latest',
                'models/gemini-1.5-pro',
                'models/gemini-2.0-pro-exp'
            ]
            
            selected_model = None
            for model_name in preferred_models:
                if model_name in model_names:
                    selected_model = model_name
                    break
            
            if not selected_model:
                logger.error("利用可能なGeminiモデルが見つかりません")
                return None
            
            self.model = genai.GenerativeModel(selected_model)
            logger.info(f"Gemini APIの初期化に成功: {selected_model}")
        except Exception as e:
            logger.error(f"Gemini APIの初期化に失敗: {str(e)}")
    
    def evolve(self):
        """進化プロセスを実行"""
        try:
            # 進化前の状態を保存
            original_content = self.host.get_content()
            
            # 進化を実行
            evolved_content = self._evolve_process(original_content)
            
            # 進化した内容を設定
            self.host.set_content(evolved_content)
            
            # 進化履歴を記録
            self._record_evolution(original_content, evolved_content)
            
        except Exception as e:
            logger.error(f"進化プロセス中にエラー: {str(e)}")
    
    def _evolve_process(self, content: str) -> str:
        """進化プロセスを実行"""
        try:
            if not self.model:
                logger.error("Geminiモデルが初期化されていません")
                return content
            
            prompt = f"""
            以下のコンテンツを改善してください：
            
            {content}
            
            改善のポイント：
            1. 文章の流れと一貫性
            2. 読者への伝わりやすさ
            3. 具体的な例示
            4. 適切な段落構成
            """
            
            logger.info("Gemini APIにリクエストを送信")
            response = self.model.generate_content(prompt)
            logger.info("Gemini APIからレスポンスを受信")
            
            if response.text:
                return response.text
            else:
                logger.error("Gemini APIからの応答が空でした")
                return content
                
        except Exception as e:
            logger.error(f"進化プロセス中にエラー: {str(e)}")
            return content
    
    def _record_evolution(self, original: str, evolved: str):
        """進化履歴を記録"""
        try:
            history = {
                "timestamp": datetime.now().isoformat(),
                "original": original,
                "evolved": evolved
            }
            
            # 進化履歴をファイルに保存
            with open("evolution_history.json", "a", encoding="utf-8") as f:
                f.write(json.dumps(history, ensure_ascii=False) + "\n")
            
            logger.info("進化履歴を記録しました")
        except Exception as e:
            logger.error(f"進化履歴の記録に失敗: {str(e)}") 