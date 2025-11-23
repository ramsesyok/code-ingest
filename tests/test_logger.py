"""
ロガーのテスト

TDDステップ1: Red - 失敗するテストを作成
"""

import logging
import tempfile
from pathlib import Path

import pytest

from src.utils.logger import setup_logger, get_logger


class TestSetupLogger:
    """setup_logger関数のテスト"""

    def test_setup_logger_creates_console_handler(self):
        """コンソールハンドラーが作成されることを確認"""
        logger = setup_logger(level="INFO")

        # StreamHandlerが存在することを確認
        console_handlers = [
            h for h in logger.handlers
            if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        ]
        assert len(console_handlers) > 0, "Console handler should be created"

    def test_setup_logger_creates_file_handler(self, tmp_path):
        """ファイルハンドラーが作成されることを確認"""
        log_file = tmp_path / "test.log"
        logger = setup_logger(level="INFO", log_file=str(log_file))

        # FileHandlerが存在することを確認
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0, "File handler should be created"
        assert log_file.exists(), "Log file should be created"

    def test_setup_logger_sets_log_level(self):
        """ログレベルが正しく設定されることを確認"""
        # DEBUGレベル
        logger = setup_logger(level="DEBUG")
        assert logger.level == logging.DEBUG

        # INFOレベル
        logger = setup_logger(level="INFO")
        assert logger.level == logging.INFO

        # WARNレベル
        logger = setup_logger(level="WARN")
        assert logger.level == logging.WARN

        # ERRORレベル
        logger = setup_logger(level="ERROR")
        assert logger.level == logging.ERROR

    def test_log_format_is_correct(self, tmp_path, caplog):
        """ログフォーマットが仕様通りであることを確認

        フォーマット: [TIMESTAMP] [LEVEL] [COMPONENT] MESSAGE
        """
        log_file = tmp_path / "format_test.log"
        logger = setup_logger(level="INFO", log_file=str(log_file))

        # テストメッセージをログ出力
        test_message = "Test message"
        logger.info(test_message)

        # ファイルに書き込まれた内容を確認
        log_content = log_file.read_text()

        # フォーマットの確認（正規表現で検証）
        import re
        # [2025-11-23 10:30:45] [INFO] [root] Test message のような形式
        pattern = r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \[INFO\] \[.*?\] Test message"
        assert re.search(pattern, log_content), f"Log format incorrect: {log_content}"


class TestGetLogger:
    """get_logger関数のテスト"""

    def test_get_logger_returns_logger(self):
        """モジュール別ロガーが取得できることを確認"""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger_returns_same_instance(self):
        """同じ名前で呼び出すと同じインスタンスが返されることを確認"""
        logger1 = get_logger("same_module")
        logger2 = get_logger("same_module")
        assert logger1 is logger2

    def test_get_logger_inherits_root_config(self):
        """get_loggerで取得したロガーがルートロガーの設定を継承することを確認"""
        # ルートロガーを設定
        setup_logger(level="DEBUG")

        # モジュール別ロガーを取得
        module_logger = get_logger("test.module")

        # ルートロガーの設定を継承していることを確認
        # (ハンドラーは伝播するため、独自のハンドラーを持たなくてもログ出力可能)
        assert module_logger.level == logging.NOTSET or module_logger.level <= logging.DEBUG
