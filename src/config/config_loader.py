"""
設定ファイルローダー

TDDステップ4: Refactor - コードの改善
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List

import yaml


@dataclass
class InputConfig:
    """入力設定"""
    source_dir: str
    ignore_file: str = ".ragignore"


@dataclass
class QdrantConfig:
    """Qdrant設定"""
    url: str
    api_key: Optional[str] = None
    collection_name: Optional[str] = None


@dataclass
class EmbeddingConfig:
    """埋め込みモデル設定"""
    model_name: str
    dimension: int
    max_length: int
    batch_size: int = 8


@dataclass
class ProcessingConfig:
    """処理設定"""
    parallel_workers: Optional[int] = None
    languages: Optional[List[str]] = None


@dataclass
class LoggingConfig:
    """ログ設定"""
    level: str = "INFO"
    file: Optional[str] = None


@dataclass
class Config:
    """全体設定"""
    input: InputConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


def _expand_env_vars(value: str) -> str:
    """
    文字列内の環境変数を展開する

    Args:
        value: 環境変数を含む可能性のある文字列

    Returns:
        環境変数が展開された文字列
    """
    if not isinstance(value, str):
        return value

    # ${VAR_NAME} 形式の環境変数を展開
    pattern = r'\$\{([^}]+)\}'

    def replace_env(match):
        env_var = match.group(1)
        return os.environ.get(env_var, match.group(0))

    return re.sub(pattern, replace_env, value)


def _expand_env_vars_recursive(data: dict) -> dict:
    """
    辞書内の全ての文字列値に対して環境変数を展開する

    Args:
        data: 設定辞書

    Returns:
        環境変数が展開された辞書
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = _expand_env_vars_recursive(value)
        elif isinstance(value, str):
            result[key] = _expand_env_vars(value)
        else:
            result[key] = value
    return result


def _validate_source_dir(source_dir: str) -> None:
    """source_dirの存在を確認"""
    if source_dir and not Path(source_dir).exists():
        raise ValueError(f"source_dir does not exist: {source_dir}")


def _validate_url(url: str) -> None:
    """URLフォーマットを確認"""
    if url and not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError(f"Invalid URL format: {url}")


def _validate_log_level(log_level: str) -> None:
    """ログレベルの妥当性を確認"""
    valid_log_levels = ["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"]
    if log_level.upper() not in valid_log_levels:
        raise ValueError(f"Invalid log level: {log_level}")


def _validate_config(config_dict: dict) -> None:
    """
    設定内容のバリデーションを行う

    Args:
        config_dict: 設定辞書

    Raises:
        ValueError: バリデーションエラー
    """
    source_dir = config_dict.get("input", {}).get("source_dir")
    _validate_source_dir(source_dir)

    url = config_dict.get("qdrant", {}).get("url")
    _validate_url(url)

    log_level = config_dict.get("logging", {}).get("level", "INFO")
    _validate_log_level(log_level)


def load_config(config_path: str) -> Config:
    """
    YAML設定ファイルを読み込む

    Args:
        config_path: 設定ファイルのパス

    Returns:
        設定オブジェクト

    Raises:
        FileNotFoundError: ファイルが存在しない
        ValueError: バリデーションエラー
    """
    # ファイルの存在確認
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # YAMLファイルの読み込み
    with open(path, "r", encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)

    # 環境変数の展開
    config_dict = _expand_env_vars_recursive(config_dict)

    # バリデーション
    _validate_config(config_dict)

    # データクラスへの変換
    return _build_config(config_dict)


def _build_config(config_dict: dict) -> Config:
    """
    辞書からConfigオブジェクトを構築する

    Args:
        config_dict: 設定辞書

    Returns:
        Configオブジェクト
    """
    return Config(
        input=InputConfig(**config_dict["input"]),
        qdrant=QdrantConfig(**config_dict["qdrant"]),
        embedding=EmbeddingConfig(**config_dict["embedding"]),
        processing=ProcessingConfig(**config_dict.get("processing", {})),
        logging=LoggingConfig(**config_dict.get("logging", {}))
    )
