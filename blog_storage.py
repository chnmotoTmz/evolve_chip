import os
import json
from typing import List, Dict
from loguru import logger

class BlogStorage:
    def __init__(self):
        self.storage_dir = "blogs"
        self._ensure_storage_dir()
        logger.info("ブログストレージを初期化しました")
    
    def _ensure_storage_dir(self):
        """ストレージディレクトリが存在することを確認します"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            logger.info(f"ストレージディレクトリを作成: {self.storage_dir}")
    
    def save_blog(self, blog_id: str, content: List[str]):
        """ブログを保存します"""
        try:
            file_path = os.path.join(self.storage_dir, f"{blog_id}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(content))
            logger.info(f"ブログを保存: {blog_id}")
        except Exception as e:
            logger.error(f"ブログの保存に失敗: {str(e)}")
            raise
    
    def load_blog(self, blog_id: str) -> List[str]:
        """ブログを読み込みます"""
        try:
            file_path = os.path.join(self.storage_dir, f"{blog_id}.txt")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().split("\n")
            logger.info(f"ブログを読み込み: {blog_id}")
            return content
        except Exception as e:
            logger.error(f"ブログの読み込みに失敗: {str(e)}")
            raise
    
    def list_blogs(self) -> List[str]:
        """利用可能なブログのリストを返します"""
        try:
            self._ensure_storage_dir()
            blog_files = [f[:-4] for f in os.listdir(self.storage_dir) 
                         if f.endswith(".txt")]
            logger.info(f"ブログ一覧を取得: {blog_files}")
            return sorted(blog_files)
        except Exception as e:
            logger.error(f"ブログ一覧の取得に失敗: {str(e)}")
            raise

def main():
    """テスト用のメイン関数"""
    logger.info("ブログストレージのテストを開始")
    storage = BlogStorage()
    
    # テストブログを作成
    test_blog_id = "test_blog"
    test_content = ["# テストブログ", "", "これはテストブログです。"]
    
    # 保存と読み込みをテスト
    storage.save_blog(test_blog_id, test_content)
    loaded_content = storage.load_blog(test_blog_id)
    assert loaded_content == test_content
    
    # ブログ一覧を取得
    blogs = storage.list_blogs()
    assert test_blog_id in blogs
    
    logger.info("テスト完了")

if __name__ == "__main__":
    main()
