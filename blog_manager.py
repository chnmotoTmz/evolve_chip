import os
from typing import List, Dict
from loguru import logger
import google.generativeai as genai
from dotenv import load_dotenv

class BlogManager:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            logger.info("Google AI APIを初期化しました")
        else:
            logger.warning("Google API Keyが設定されていません")
        
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.blogs: Dict[str, List[str]] = {}
        
        # ログの設定
        logger.add("blog_manager.log", rotation="500 MB")
    
    def add_blog(self, blog_id: str, content: List[str]) -> bool:
        """新しいブログを追加します"""
        try:
            # ブログの内容を検証
            if not content or not any(line.strip().startswith("#") for line in content):
                logger.error("ブログにタイトルがありません")
                return False
            
            logger.info(f"ブログを追加: {blog_id}")
            self.blogs[blog_id] = content
            return True
        except Exception as e:
            logger.error(f"ブログの追加に失敗: {str(e)}")
            return False
    
    def evolve_blog(self, content: List[str]) -> List[str]:
        """ブログの内容を進化させます"""
        try:
            if not self.api_key:
                logger.error("Google API Keyが設定されていません")
                return content
            
            # 進化のプロンプトを作成
            blog_content = "\n".join(content)
            prompt = (
                "以下のブログ記事を改善してください：\n\n"
                f"{blog_content}\n\n"
                "改善点：\n"
                "1. より詳細な説明の追加\n"
                "2. 文章の流れの改善\n"
                "3. 専門用語の適切な使用\n"
                "4. 読みやすさの向上\n\n"
                "元の形式を保持したまま、内容を改善した記事を返してください。"
            )
            
            # 進化を実行
            response = self.model.generate_content(prompt)
            
            # レスポンスを処理
            if response.text:
                evolved_content = response.text.strip().split("\n")
                logger.info("ブログを進化させました")
                return evolved_content
            else:
                logger.warning("進化に失敗しました")
                return content
        except Exception as e:
            logger.error(f"進化プロセスでエラー: {str(e)}")
            return content
    
    def get_blog(self, blog_id: str, content: List[str]) -> Dict:
        """ブログの情報を取得します"""
        try:
            title = next((line.strip("#").strip() for line in content 
                         if line.strip().startswith("#")), "無題")
            
            return {
                "id": blog_id,
                "title": title,
                "content": content,
                "length": len(content)
            }
        except Exception as e:
            logger.error(f"ブログ情報の取得に失敗: {str(e)}")
            return {
                "id": blog_id,
                "title": "エラー",
                "content": [],
                "length": 0
            }

def main():
    """テスト用のメイン関数"""
    logger.info("ブログマネージャーのテストを開始")
    manager = BlogManager()
    
    # テストブログを作成
    test_content = [
        "# テストブログ",
        "",
        "これはテストブログです。",
        "ブログの内容を進化させることができます。"
    ]
    
    # ブログの追加をテスト
    success = manager.add_blog("test_blog", test_content)
    assert success
    
    # ブログの進化をテスト
    evolved_content = manager.evolve_blog(test_content)
    assert len(evolved_content) > 0
    
    # ブログ情報の取得をテスト
    blog_info = manager.get_blog("test_blog", test_content)
    assert blog_info["title"] == "テストブログ"
    
    logger.info("テスト完了")

if __name__ == "__main__":
    main()
