"""
パーサー基底クラスとFunctionInfo

TDDステップ2-3: Green - テストを通す実装
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class FunctionInfo:
    """関数・メソッドの情報を保持するデータクラス"""

    # 基本情報
    name: str                           # 関数名
    code: str                           # コード全体（コメント含む）
    file_path: str                      # ファイルパス
    start_line: int                     # 開始行
    end_line: int                       # 終了行
    start_column: int                   # 開始列
    end_column: int                     # 終了列
    language: str                       # 言語名（python/rust/go/java/c/cpp）

    # 構文要素
    function_type: str = "function"     # 関数タイプ（function/method/class）
    arguments: List[str] = field(default_factory=list)  # 引数リスト
    return_type: Optional[str] = None   # 戻り値の型

    # ドキュメント
    docstring: Optional[str] = None     # ドキュメント文字列
    comments: List[str] = field(default_factory=list)  # コメント

    # 修飾子・スコープ
    modifiers: List[str] = field(default_factory=list)  # 修飾子（public/private/static等）
    scope: str = "global"               # スコープ（global/class/local）

    # 依存関係
    imports: List[str] = field(default_factory=list)    # import/include文
    calls: List[str] = field(default_factory=list)      # 呼び出す関数リスト

    # メトリクス
    complexity: Optional[int] = None    # サイクロマティック複雑度
    loc: int = 0                        # 実効行数（Lines of Code）
    comment_lines: int = 0              # コメント行数


class BaseParser(ABC):
    """パーサー基底クラス"""

    @abstractmethod
    def parse_file(self, file_path: Path) -> List[FunctionInfo]:
        """
        ファイルを解析して関数情報リストを返す

        Args:
            file_path: 解析対象ファイル

        Returns:
            FunctionInfoのリスト

        Raises:
            SyntaxError: 構文エラー（サブクラスで処理）
        """
        pass

    @abstractmethod
    def get_language(self) -> str:
        """
        対応言語名を返す

        Returns:
            言語名（python/rust/go/java/c/cpp）
        """
        pass

    # 共通ユーティリティメソッド（実装済み）

    def _count_lines(self, code: str) -> tuple[int, int]:
        """
        実効行数とコメント行数をカウント

        Args:
            code: ソースコード

        Returns:
            (実効行数, コメント行数)
        """
        lines = code.split('\n')
        loc = 0
        comment_lines = 0

        for line in lines:
            stripped = line.strip()

            # 空行はスキップ
            if not stripped:
                continue

            # コメント行の判定（簡易実装）
            if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                comment_lines += 1
            else:
                loc += 1

        return loc, comment_lines

    def _calculate_complexity(self, code: str) -> int:
        """
        サイクロマティック複雑度を計算

        簡易実装: 分岐文（if/for/while/elif/else/case/switch等）の数 + 1

        Args:
            code: ソースコード

        Returns:
            サイクロマティック複雑度
        """
        # 制御構造のキーワード
        control_keywords = [
            r'\bif\b',
            r'\bfor\b',
            r'\bwhile\b',
            r'\belif\b',
            r'\belse\b',
            r'\bcase\b',
            r'\bswitch\b',
            r'\bcatch\b',
            r'\b\?\b',  # 三項演算子
        ]

        complexity = 1  # 基本複雑度

        for keyword_pattern in control_keywords:
            matches = re.findall(keyword_pattern, code)
            complexity += len(matches)

        return complexity
