"""
ロガー設定モジュール

TDDステップ4: Refactor - コードの改善
"""

import logging
import sys
from pathlib import Path
from typing import Optional


# ログフォーマット: [TIMESTAMP] [LEVEL] [COMPONENT] MESSAGE
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _create_formatter() -> logging.Formatter:
    """ログフォーマッターを作成する"""
    return logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)


def _create_console_handler(log_level: int) -> logging.StreamHandler:
    """コンソールハンドラーを作成する"""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(_create_formatter())
    return handler


def _create_file_handler(log_file: str, log_level: int) -> logging.FileHandler:
    """ファイルハンドラーを作成する"""
    # ログファイルのディレクトリを作成
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setLevel(log_level)
    handler.setFormatter(_create_formatter())
    return handler


def setup_logger(
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    ルートロガーをセットアップする

    Args:
        level: ログレベル (DEBUG, INFO, WARN, ERROR)
        log_file: ログファイルのパス (オプション)

    Returns:
        設定済みのルートロガー
    """
    # ログレベルの変換
    log_level = getattr(logging, level.upper())

    # ルートロガーを取得
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 既存のハンドラーをクリア（重複を防ぐ）
    root_logger.handlers.clear()

    # コンソールハンドラーの追加
    root_logger.addHandler(_create_console_handler(log_level))

    # ファイルハンドラーの追加（指定された場合）
    if log_file:
        root_logger.addHandler(_create_file_handler(log_file, log_level))

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    モジュール別のロガーを取得する

    Args:
        name: ロガー名（通常はモジュール名）

    Returns:
        指定された名前のロガー
    """
    return logging.getLogger(name)
