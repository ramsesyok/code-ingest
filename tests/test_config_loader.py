"""
設定ファイルローダーのテスト

TDDステップ1: Red - 失敗するテストを作成
"""

import os
from pathlib import Path

import pytest

from src.config.config_loader import (
    Config,
    InputConfig,
    QdrantConfig,
    EmbeddingConfig,
    ProcessingConfig,
    LoggingConfig,
    load_config,
)


class TestLoadConfig:
    """load_config関数のテスト"""

    def test_load_valid_config(self):
        """正常な設定ファイルを読み込めることを確認"""
        config_path = Path(__file__).parent / "fixtures" / "valid_config.yaml"
        config = load_config(str(config_path))

        assert isinstance(config, Config)
        assert config.input.source_dir == "/tmp/test_source"
        assert config.input.ignore_file == ".ragignore"
        assert config.qdrant.url == "http://localhost:6333"
        assert config.qdrant.collection_name == "test-collection"
        assert config.embedding.model_name == "jinaai/jina-embeddings-v2-base-code"
        assert config.embedding.dimension == 768
        assert config.processing.parallel_workers == 4
        assert config.processing.languages == ["python", "rust", "go"]
        assert config.logging.level == "INFO"

    def test_load_missing_file_raises_error(self):
        """存在しないファイルでFileNotFoundErrorが発生することを確認"""
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/config.yaml")

    def test_expand_env_vars(self, monkeypatch):
        """環境変数が展開されることを確認"""
        # 環境変数を設定
        monkeypatch.setenv("QDRANT_API_KEY", "test-api-key-12345")

        config_path = Path(__file__).parent / "fixtures" / "valid_config.yaml"
        config = load_config(str(config_path))

        # 環境変数が展開されているか確認
        assert config.qdrant.api_key == "test-api-key-12345"

    def test_default_values(self):
        """デフォルト値が適用されることを確認"""
        config_path = Path(__file__).parent / "fixtures" / "minimal_config.yaml"
        config = load_config(str(config_path))

        # デフォルト値の確認
        assert config.input.ignore_file == ".ragignore"  # デフォルト
        assert config.qdrant.api_key is None  # 環境変数未設定時はNone
        assert config.qdrant.collection_name is None  # デフォルトはNone（後で自動生成）
        assert config.processing.parallel_workers is None  # デフォルトはNone（CPU数）
        assert config.processing.languages is None  # デフォルトはNone（全言語）
        assert config.logging.level == "INFO"  # デフォルト
        assert config.logging.file is None  # デフォルトはNone

    def test_collection_name_defaults_to_dirname(self):
        """collection_name未指定時にディレクトリ名が使われることを確認"""
        config_path = Path(__file__).parent / "fixtures" / "minimal_config.yaml"
        config = load_config(str(config_path))

        # この時点ではNone（実際のディレクトリ名への変換は別処理で行う）
        assert config.qdrant.collection_name is None

    def test_validate_invalid_source_dir(self, tmp_path):
        """存在しないsource_dirで例外が発生することを確認"""
        # 存在しないディレクトリを指定した設定ファイルを作成
        invalid_config = tmp_path / "invalid_source.yaml"
        invalid_config.write_text("""
input:
  source_dir: "/nonexistent/directory/path"

qdrant:
  url: "http://localhost:6333"

embedding:
  model_name: "jinaai/jina-embeddings-v2-base-code"
  dimension: 768
  max_length: 8192
""")

        with pytest.raises(ValueError, match="source_dir does not exist"):
            load_config(str(invalid_config))

    def test_validate_invalid_url(self, tmp_path):
        """不正なURL形式で例外が発生することを確認"""
        invalid_config = tmp_path / "invalid_url.yaml"
        # 一時的なディレクトリを作成
        test_dir = tmp_path / "test_source"
        test_dir.mkdir()

        invalid_config.write_text(f"""
input:
  source_dir: "{test_dir}"

qdrant:
  url: "invalid-url-format"

embedding:
  model_name: "jinaai/jina-embeddings-v2-base-code"
  dimension: 768
  max_length: 8192
""")

        with pytest.raises(ValueError, match="Invalid URL format"):
            load_config(str(invalid_config))

    def test_validate_invalid_log_level(self, tmp_path):
        """不正なログレベルで例外が発生することを確認"""
        invalid_config = tmp_path / "invalid_log_level.yaml"
        test_dir = tmp_path / "test_source"
        test_dir.mkdir()

        invalid_config.write_text(f"""
input:
  source_dir: "{test_dir}"

qdrant:
  url: "http://localhost:6333"

embedding:
  model_name: "jinaai/jina-embeddings-v2-base-code"
  dimension: 768
  max_length: 8192

logging:
  level: "INVALID_LEVEL"
""")

        with pytest.raises(ValueError, match="Invalid log level"):
            load_config(str(invalid_config))

    def test_validate_missing_required_fields(self):
        """必須フィールドが欠けている場合に例外が発生することを確認"""
        config_path = Path(__file__).parent / "fixtures" / "invalid_config.yaml"

        with pytest.raises((KeyError, ValueError)):
            load_config(str(config_path))


class TestConfigDataClasses:
    """設定データクラスのテスト"""

    def test_input_config_creation(self):
        """InputConfigが作成できることを確認"""
        input_config = InputConfig(
            source_dir="/tmp/test",
            ignore_file=".ragignore"
        )
        assert input_config.source_dir == "/tmp/test"
        assert input_config.ignore_file == ".ragignore"

    def test_qdrant_config_creation(self):
        """QdrantConfigが作成できることを確認"""
        qdrant_config = QdrantConfig(
            url="http://localhost:6333",
            api_key="test-key",
            collection_name="test-collection"
        )
        assert qdrant_config.url == "http://localhost:6333"
        assert qdrant_config.api_key == "test-key"
        assert qdrant_config.collection_name == "test-collection"

    def test_embedding_config_creation(self):
        """EmbeddingConfigが作成できることを確認"""
        embedding_config = EmbeddingConfig(
            model_name="test-model",
            dimension=768,
            max_length=8192,
            batch_size=8
        )
        assert embedding_config.model_name == "test-model"
        assert embedding_config.dimension == 768

    def test_processing_config_creation(self):
        """ProcessingConfigが作成できることを確認"""
        processing_config = ProcessingConfig(
            parallel_workers=4,
            languages=["python", "rust"]
        )
        assert processing_config.parallel_workers == 4
        assert processing_config.languages == ["python", "rust"]

    def test_logging_config_creation(self):
        """LoggingConfigが作成できることを確認"""
        logging_config = LoggingConfig(
            level="DEBUG",
            file="test.log"
        )
        assert logging_config.level == "DEBUG"
        assert logging_config.file == "test.log"

    def test_config_creation(self):
        """Configが作成できることを確認"""
        config = Config(
            input=InputConfig(source_dir="/tmp", ignore_file=".ragignore"),
            qdrant=QdrantConfig(url="http://localhost:6333"),
            embedding=EmbeddingConfig(
                model_name="test",
                dimension=768,
                max_length=8192
            ),
            processing=ProcessingConfig(),
            logging=LoggingConfig()
        )
        assert isinstance(config.input, InputConfig)
        assert isinstance(config.qdrant, QdrantConfig)
        assert isinstance(config.embedding, EmbeddingConfig)
