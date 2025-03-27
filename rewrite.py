import os
import subprocess
import sys
import psutil
from typing import List
from loguru import logger
from evolve_module import get_evolved_content, validate_evolution
import json
from datetime import datetime
import platform

def stop_app():
    """アプリケーションを停止します"""
    try:
        current_pid = os.getpid()
        stopped_pids = []
        process_info = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['pid'] != current_pid and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and 'main.py' in cmdline:
                        proc_info = {
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cmdline": cmdline,
                            "cpu_percent": proc.info['cpu_percent'],
                            "memory_percent": proc.info['memory_percent']
                        }
                        proc.terminate()
                        stopped_pids.append(proc.info['pid'])
                        process_info.append(proc_info)
                        logger.info(f"アプリケーションを停止しました: {json.dumps(proc_info, ensure_ascii=False)}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not stopped_pids:
            logger.warning("停止するアプリケーションが見つかりませんでした")
        else:
            logger.info(f"停止したプロセス数: {len(stopped_pids)}")
            
    except Exception as e:
        logger.error(f"アプリケーションの停止に失敗: {str(e)}")

def rewrite_blog(blog_id: str, evolution_suggestion: str):
    """ブログ記事を書き換えます"""
    try:
        # 進化提案の検証
        if not validate_evolution(evolution_suggestion):
            logger.error(f"進化提案が無効です: {blog_id}")
            return False
        
        # 元のブログ記事を読み込み
        from blog_storage import BlogStorage
        storage = BlogStorage()
        original_content = storage.load_blog(blog_id)
        
        if not original_content:
            logger.error(f"ブログ記事が見つかりません: {blog_id}")
            return False
        
        # 進化提案を適用
        evolved_content = get_evolved_content(original_content, evolution_suggestion)
        
        # 新しい内容を保存
        storage.save_blog(blog_id, evolved_content)
        
        # 書き換えの詳細をログに記録
        rewrite_log = {
            "timestamp": datetime.now().isoformat(),
            "blog_id": blog_id,
            "original_length": len(original_content),
            "evolved_length": len(evolved_content),
            "evolution_suggestion": evolution_suggestion,
            "system_info": {
                "platform": platform.platform(),
                "python_version": sys.version,
                "working_directory": os.getcwd()
            },
            "file_info": {
                "blog_file": storage.get_blog_path(blog_id),
                "file_size": os.path.getsize(storage.get_blog_path(blog_id)) if os.path.exists(storage.get_blog_path(blog_id)) else 0
            }
        }
        
        logger.info(f"ブログ記事を書き換えました: {json.dumps(rewrite_log, ensure_ascii=False)}")
        return True
    except Exception as e:
        logger.error(f"ブログ記事の書き換えに失敗: {str(e)}")
        return False

def main():
    if len(sys.argv) < 3:
        logger.error("引数が不足しています")
        print("使用法: python rewrite.py <ブログID> \"<進化提案>\"")
        sys.exit(1)
    
    blog_id = sys.argv[1]
    evolution_suggestion = sys.argv[2]
    
    # 実行開始をログに記録
    start_log = {
        "timestamp": datetime.now().isoformat(),
        "command": " ".join(sys.argv),
        "blog_id": blog_id,
        "evolution_suggestion_length": len(evolution_suggestion)
    }
    logger.info(f"ブログ書き換えを開始: {json.dumps(start_log, ensure_ascii=False)}")
    
    # アプリケーションを停止
    stop_app()
    
    # ブログ記事を書き換え
    if rewrite_blog(blog_id, evolution_suggestion):
        # アプリケーションを再起動
        new_process = subprocess.Popen(["python", "main.py"])
        restart_log = {
            "timestamp": datetime.now().isoformat(),
            "new_pid": new_process.pid,
            "command": "python main.py"
        }
        logger.info(f"アプリケーションを再起動しました: {json.dumps(restart_log, ensure_ascii=False)}")
    else:
        logger.error("ブログ記事の書き換えに失敗しました")

if __name__ == "__main__":
    main() 