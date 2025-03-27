import ast
from typing import List, Dict
from loguru import logger
import json
from datetime import datetime
import difflib

def get_evolved_content(original_content: List[str], evolution_suggestion: str) -> List[str]:
    """元のブログ記事に進化提案を適用した新しい記事を返す"""
    try:
        # 進化提案の安全性チェック
        if any(keyword in evolution_suggestion.lower() for keyword in ["import", "exec", "eval", "os.", "sys."]):
            logger.warning(f"安全でないコードを含む進化提案を拒否: {evolution_suggestion}")
            raise ValueError("安全でないコードを含む進化提案を拒否しました")
        
        # 進化提案を適用
        evolved_lines = []
        title_found = False
        changes_count = 0
        changed_lines = []
        
        for i, line in enumerate(original_content):
            if line.strip().startswith("#"):
                # タイトル行はそのまま保持
                evolved_lines.append(line)
                title_found = True
            elif title_found and line.strip():
                # 本文の最初の段落を進化提案で置き換え
                evolved_lines.append(evolution_suggestion)
                title_found = False
                changes_count += 1
                changed_lines.append({
                    "line_number": i + 1,
                    "original": line,
                    "evolved": evolution_suggestion
                })
            else:
                # その他の行はそのまま保持
                evolved_lines.append(line)
        
        # 差分を計算
        diff = list(difflib.unified_diff(original_content, evolved_lines, lineterm=''))
        
        # 進化の詳細をログに記録
        evolution_log = {
            "timestamp": datetime.now().isoformat(),
            "original_length": len(original_content),
            "evolved_length": len(evolved_lines),
            "changes_count": changes_count,
            "changed_lines": changed_lines,
            "diff": diff,
            "evolution_suggestion": evolution_suggestion,
            "metadata": {
                "title": next((line for line in original_content if line.strip().startswith("#")), ""),
                "original_paragraphs": len([line for line in original_content if line.strip() and not line.strip().startswith("#")]),
                "evolved_paragraphs": len([line for line in evolved_lines if line.strip() and not line.strip().startswith("#")])
            }
        }
        
        logger.info(f"ブログ記事の進化に成功: {json.dumps(evolution_log, ensure_ascii=False)}")
        return evolved_lines
    except Exception as e:
        logger.error(f"ブログ記事の進化に失敗: {str(e)}")
        return original_content  # 失敗時は元の記事を返す

def validate_evolution(evolution_suggestion: str) -> bool:
    """進化提案の妥当性を検証します"""
    try:
        # 基本的な検証
        if not evolution_suggestion.strip():
            logger.warning("空の進化提案を拒否")
            return False
        
        # 長さの制限
        if len(evolution_suggestion) > 1000:  # 例: 1000文字まで
            logger.warning(f"進化提案が長すぎます: {len(evolution_suggestion)}文字")
            return False
        
        # 禁止キーワードのチェック
        forbidden_keywords = ["import", "exec", "eval", "os.", "sys."]
        found_keywords = [kw for kw in forbidden_keywords if kw in evolution_suggestion.lower()]
        if found_keywords:
            logger.warning(f"禁止キーワードを含む進化提案を拒否: {found_keywords}")
            return False
        
        logger.info(f"進化提案の検証に成功: {len(evolution_suggestion)}文字")
        return True
    except Exception as e:
        logger.error(f"進化提案の検証に失敗: {str(e)}")
        return False

def main():
    # テスト用のメイン関数
    test_content = [
        "# 私のブログ",
        "こんにちは、世界！",
        "今日は素晴らしい一日でした。"
    ]
    
    evolution_suggestion = "こんにちは、世界！今日は素晴らしい一日でした。新しい発見がありました。"
    
    if validate_evolution(evolution_suggestion):
        evolved_content = get_evolved_content(test_content, evolution_suggestion)
        logger.info(f"進化後のブログ: {json.dumps(evolved_content, ensure_ascii=False)}")
    else:
        logger.warning("進化提案が無効です")

if __name__ == "__main__":
    main() 