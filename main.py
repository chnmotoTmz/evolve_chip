import tkinter as tk
from tkinter import ttk, scrolledtext
from loguru import logger
from blog import Blog

class BlogApp:
    """ブログアプリケーションのGUI"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AIチップブログ")
        self.root.geometry("800x600")
        
        # ブログの初期化
        self.blog = Blog(
            title="テスト記事",
            content="これはテスト用のブログ記事です。\n\nAIによって進化させることができます。"
        )
        
        self.setup_ui()
    
    def setup_ui(self):
        """UIの初期化"""
        # タイトル入力
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(title_frame, text="タイトル:").pack(side=tk.LEFT)
        self.title_entry = ttk.Entry(title_frame)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.title_entry.insert(0, self.blog.title)
        
        # タグ入力
        tag_frame = ttk.Frame(self.root)
        tag_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(tag_frame, text="タグ:").pack(side=tk.LEFT)
        self.tag_entry = ttk.Entry(tag_frame)
        self.tag_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(tag_frame, text="追加", command=self.add_tag).pack(side=tk.LEFT, padx=5)
        
        # タグ表示
        self.tag_listbox = tk.Listbox(self.root, height=3)
        self.tag_listbox.pack(fill=tk.X, padx=5, pady=2)
        for tag in self.blog.tags:
            self.tag_listbox.insert(tk.END, tag)
        
        # 方向性の説明
        ttk.Label(self.root, 
                 text="ブログの進化方向をコメントとして入力してください。\n例：「より技術的な内容に」「読みやすく」「SEO対策を意識して」など").pack(padx=5, pady=2)
        
        # 方向性入力エリア
        self.direction_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=3)
        self.direction_text.pack(fill=tk.X, padx=5, pady=5)
        
        # ブログ編集エリア
        self.content_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=20)
        self.content_text.pack(expand=True, fill='both', padx=5, pady=5)
        self.content_text.insert('1.0', self.blog.get_content())
        
        # ボタンエリア
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="進化", command=self.evolve).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="公開", command=self.publish).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存", command=self.save).pack(side=tk.LEFT, padx=5)
    
    def add_tag(self):
        """タグを追加"""
        tag = self.tag_entry.get().strip()
        if tag:
            self.blog.add_tag(tag)
            self.tag_listbox.insert(tk.END, tag)
            self.tag_entry.delete(0, tk.END)
    
    def evolve(self):
        """進化を実行"""
        self.blog.embed_chip()
        self.blog.update()
        self.update_content()
    
    def publish(self):
        """ブログを公開"""
        self.blog.title = self.title_entry.get()
        self.blog.content = self.content_text.get('1.0', tk.END).strip()
        self.blog.publish()
    
    def save(self):
        """ブログを保存"""
        self.blog.title = self.title_entry.get()
        self.blog.content = self.content_text.get('1.0', tk.END).strip()
        logger.info("ブログを保存しました")
    
    def update_content(self):
        """コンテンツを更新"""
        self.content_text.delete('1.0', tk.END)
        self.content_text.insert('1.0', self.blog.get_content())
    
    def run(self):
        """アプリケーションを実行"""
        self.root.mainloop()

def main():
    """メイン関数"""
    app = BlogApp()
    app.run()

if __name__ == "__main__":
    main() 