import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from blog_manager import BlogManager
from blog_storage import BlogStorage
from loguru import logger
import sys

class BlogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ブログ管理システム")
        self.root.geometry("800x600")
        
        # ロガーの設定
        logger.add("blog_app.log", rotation="500 MB")
        
        # ブログマネージャーとストレージの初期化
        self.blog_manager = BlogManager()
        self.blog_storage = BlogStorage()
        
        # AIチップの初期化
        self.evolve_chip = None
        try:
            from evolve_chip import EvolveChip
            self.evolve_chip = EvolveChip(self)
            if not self.evolve_chip.model:
                messagebox.showwarning("警告", 
                    "AIチップの初期化に失敗しました。\n"
                    "GEMINI_API_KEY環境変数が設定されているか確認してください。")
                logger.warning("AIチップの初期化に失敗しました")
        except ImportError as e:
            logger.error(f"AIチップのインポートに失敗: {str(e)}")
            messagebox.showerror("エラー", "AIチップモジュールが見つかりません")
        except Exception as e:
            logger.error(f"AIチップの初期化中にエラー: {str(e)}")
            messagebox.showerror("エラー", f"AIチップの初期化中にエラーが発生しました: {str(e)}")
        
        # UIのセットアップ
        self.setup_ui()
        
        # ブログ一覧の読み込み
        self.load_blogs()
        
        # ウィンドウのクローズイベントを設定
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup)
    
    def setup_ui(self):
        """UIコンポーネントをセットアップします"""
        # ブログ選択
        blog_frame = ttk.Frame(self.root)
        blog_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(blog_frame, text="ブログ:").pack(side=tk.LEFT)
        self.blog_var = tk.StringVar()
        self.blog_combo = ttk.Combobox(blog_frame, textvariable=self.blog_var)
        self.blog_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.blog_combo.bind('<<ComboboxSelected>>', lambda e: self.load_blog())
        
        # 進化の方向性設定
        direction_frame = ttk.LabelFrame(self.root, text="進化の方向性")
        direction_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 方向性の説明
        ttk.Label(direction_frame, 
                 text="ブログの進化方向をコメントとして入力してください。\n例：「より技術的な内容に」「読みやすく」「SEO対策を意識して」など").pack(padx=5, pady=2)
        
        # 方向性入力エリア
        self.direction_text = scrolledtext.ScrolledText(direction_frame, wrap=tk.WORD, height=3)
        self.direction_text.pack(fill=tk.X, padx=5, pady=5)
        
        # ブログ編集エリア
        self.content_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=20)
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ボタンフレーム
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.save_button = ttk.Button(button_frame, text="保存", command=self.save_blog)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.evolve_button = ttk.Button(button_frame, text="進化", command=self.evolve_blog)
        self.evolve_button.pack(side=tk.LEFT, padx=5)
        
        self.create_button = ttk.Button(button_frame, text="新規作成", command=self.create_new_blog)
        self.create_button.pack(side=tk.LEFT, padx=5)
        
        # 進捗表示
        self.progress_var = tk.StringVar()
        self.progress_label = ttk.Label(self.root, textvariable=self.progress_var)
        self.progress_label.pack(fill=tk.X, padx=5, pady=5)
    
    def disable_buttons(self):
        """ボタンを無効化します"""
        self.save_button["state"] = "disabled"
        self.evolve_button["state"] = "disabled"
        self.create_button["state"] = "disabled"
        self.blog_combo["state"] = "disabled"
        self.progress_var.set("進化中...")
    
    def enable_buttons(self):
        """ボタンを有効化します"""
        self.save_button["state"] = "normal"
        self.evolve_button["state"] = "normal"
        self.create_button["state"] = "normal"
        self.blog_combo["state"] = "readonly"
        self.progress_var.set("")
    
    def load_blogs(self):
        """ブログ一覧を読み込みます"""
        try:
            blogs = self.blog_storage.list_blogs()
            self.blog_combo['values'] = blogs
            if blogs:
                self.blog_combo.set(blogs[0])
                self.load_blog()
            logger.info(f"ブログ一覧を読み込み: {blogs}")
        except Exception as e:
            logger.error(f"ブログ一覧の読み込みに失敗: {str(e)}")
            messagebox.showerror("エラー", f"ブログ一覧の読み込みに失敗しました: {str(e)}")
    
    def load_blog(self):
        """選択されたブログを読み込みます"""
        try:
            blog_id = self.blog_var.get()
            if not blog_id:
                return
            
            content = self.blog_storage.load_blog(blog_id)
            self.content_text.delete('1.0', tk.END)
            self.content_text.insert('1.0', '\n'.join(content))
            logger.info(f"ブログを読み込み: {blog_id}")
        except Exception as e:
            logger.error(f"ブログの読み込みに失敗: {str(e)}")
            messagebox.showerror("エラー", f"ブログの読み込みに失敗しました: {str(e)}")
    
    def save_blog(self):
        """現在のブログを保存します"""
        try:
            blog_id = self.blog_var.get()
            if not blog_id:
                messagebox.showwarning("警告", "ブログを選択してください")
                return
            
            content = self.content_text.get('1.0', tk.END).strip().split('\n')
            self.blog_storage.save_blog(blog_id, content)
            logger.info(f"ブログを保存: {blog_id}")
            messagebox.showinfo("成功", "ブログを保存しました")
        except Exception as e:
            logger.error(f"ブログの保存に失敗: {str(e)}")
            messagebox.showerror("エラー", f"ブログの保存に失敗しました: {str(e)}")
    
    def evolve_blog(self):
        """選択されたブログを進化させます"""
        try:
            blog_id = self.blog_var.get()
            if not blog_id:
                messagebox.showwarning("警告", "ブログを選択してください")
                return
            
            if not self.evolve_chip:
                messagebox.showwarning("警告", "AIチップが利用できません")
                return
            
            # 進化の方向性をコメントとして取得
            direction_comment = self.direction_text.get('1.0', tk.END).strip()
            if not direction_comment:
                messagebox.showwarning("警告", "進化の方向性を入力してください")
                return
            
            # 進化の方向性を設定
            direction = {
                "comment": direction_comment
            }
            self.evolve_chip.set_evolution_direction(direction)
            
            logger.info(f"ブログの進化を開始: {direction_comment}")
            self.evolve_chip.start_evolving()
        except Exception as e:
            logger.error(f"ブログの進化に失敗: {str(e)}")
            messagebox.showerror("エラー", f"ブログの進化に失敗しました: {str(e)}")
    
    def create_new_blog(self):
        """新しいブログを作成します"""
        try:
            dialog = tk.Toplevel(self.root)
            dialog.title("新規ブログ作成")
            dialog.geometry("300x100")
            
            ttk.Label(dialog, text="ブログID:").pack(pady=5)
            blog_id_var = tk.StringVar()
            ttk.Entry(dialog, textvariable=blog_id_var).pack(pady=5)
            
            def create():
                blog_id = blog_id_var.get().strip()
                if not blog_id:
                    messagebox.showwarning("警告", "ブログIDを入力してください")
                    return
                
                if blog_id in self.blog_storage.list_blogs():
                    messagebox.showwarning("警告", "このブログIDは既に存在します")
                    return
                
                self.blog_storage.save_blog(blog_id, ["# " + blog_id, ""])
                self.load_blogs()
                self.blog_var.set(blog_id)
                self.load_blog()
                dialog.destroy()
                logger.info(f"新規ブログを作成: {blog_id}")
            
            ttk.Button(dialog, text="作成", command=create).pack(pady=5)
        except Exception as e:
            logger.error(f"新規ブログの作成に失敗: {str(e)}")
            messagebox.showerror("エラー", f"新規ブログの作成に失敗しました: {str(e)}")
    
    def cleanup(self):
        """アプリケーションのクリーンアップを行います"""
        try:
            # AIチップを停止
            if self.evolve_chip:
                self.evolve_chip.cleanup()
            
            # ウィンドウを破棄
            self.root.destroy()
            
            # プロセスを終了
            sys.exit(0)
        except Exception as e:
            logger.error(f"クリーンアップ中にエラー: {str(e)}")
            sys.exit(1)

def main():
    root = tk.Tk()
    app = BlogApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
