from loguru import logger
from datetime import datetime
from evolve_chip import EvolveChip

class Blog:
    """ブログ記事を管理するクラス"""
    def __init__(self, title="", content=""):
        self.title = title
        self.content = content
        self.published_date = None
        self.tags = []
        self.chip = None
    
    def get_content(self):
        """コンテンツを取得"""
        return self.content
    
    def set_content(self, content):
        """コンテンツを設定"""
        self.content = content
    
    def embed_chip(self):
        """AIチップを埋め込む"""
        if self.chip is None:
            try:
                self.chip = EvolveChip(self)
                logger.info("AIチップを埋め込みました")
            except Exception as e:
                logger.error(f"AIチップの埋め込みに失敗: {e}")
    
    def update(self):
        """更新時に進化を実行"""
        if self.chip:
            self.chip.evolve()
    
    def publish(self):
        """ブログを公開"""
        self.published_date = datetime.now()
        logger.info(f"ブログ「{self.title}」を公開しました")
    
    def add_tag(self, tag):
        """タグを追加"""
        if tag not in self.tags:
            self.tags.append(tag)
            logger.info(f"タグ「{tag}」を追加しました")
    
    def remove_tag(self, tag):
        """タグを削除"""
        if tag in self.tags:
            self.tags.remove(tag)
            logger.info(f"タグ「{tag}」を削除しました") 