"""
パーサーファクトリ

TDDステップ4-4: Green - テストを通す実装
"""

from pathlib import Path
from typing import Dict, Optional

from src.parser.base_parser import BaseParser
from src.parser.python_parser import PythonParser
from src.parser.rust_parser import RustParser
from src.parser.go_parser import GoParser
from src.parser.java_parser import JavaParser
from src.parser.c_parser import CParser
from src.parser.cpp_parser import CppParser


class ParserFactory:
    """パーサーファクトリ（シングルトンパターン）"""

    def __init__(self):
        """遅延初期化（get_parserで初回アクセス時に初期化）"""
        self._parsers: Dict[str, BaseParser] = {}
        self._initialized = False

    def _initialize_parsers(self):
        """パーサーインスタンスを初期化"""
        if not self._initialized:
            self._parsers = {
                'python': PythonParser(),
                'rust': RustParser(),
                'go': GoParser(),
                'java': JavaParser(),
                'c': CParser(),
                'cpp': CppParser()
            }
            self._initialized = True

    def get_parser(self, file_path: Path) -> Optional[BaseParser]:
        """
        ファイルパスからパーサーを取得

        Args:
            file_path: ソースファイルパス

        Returns:
            対応するパーサー、未対応の場合None
        """
        self._initialize_parsers()
        language = self._detect_language(file_path)
        return self._parsers.get(language)

    def _detect_language(self, file_path: Path) -> Optional[str]:
        """
        拡張子から言語を判定

        Args:
            file_path: ファイルパス

        Returns:
            言語名（python/rust/go/java/c/cpp）、未対応の場合None
        """
        suffix = file_path.suffix.lower()

        extension_map = {
            '.py': 'python',
            '.rs': 'rust',
            '.go': 'go',
            '.java': 'java',
            '.c': 'c',
            '.h': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.hpp': 'cpp',
            '.hh': 'cpp',
            '.hxx': 'cpp'
        }

        return extension_map.get(suffix)
