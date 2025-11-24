"""
Goパーサー

TDDステップ2-3: Green - テストを通す実装
"""

from pathlib import Path
from typing import List

from tree_sitter import Language, Parser, Node
import tree_sitter_go

from src.parser.base_parser import BaseParser, FunctionInfo
from src.utils.logger import get_logger


logger = get_logger(__name__)


class GoParser(BaseParser):
    """Goファイル用パーサー"""

    def __init__(self):
        """Tree-sitterパーサー初期化"""
        self.language = Language(tree_sitter_go.language())
        self.parser = Parser(self.language)

    def get_language(self) -> str:
        """対応言語名を返す"""
        return "go"

    def parse_file(self, file_path: Path) -> List[FunctionInfo]:
        """
        Goファイルを解析

        Args:
            file_path: 解析対象ファイル

        Returns:
            FunctionInfoのリスト

        Raises:
            FileNotFoundError: ファイルが存在しない
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except UnicodeDecodeError as e:
            logger.warning(f"Encoding error in {file_path}: {e}")
            return []

        # Tree-sitterでパース
        tree = self.parser.parse(bytes(source_code, "utf8"))

        if tree.root_node.has_error:
            logger.warning(f"Syntax error in {file_path}")
            return []

        # AST走査
        functions = self._traverse_ast(tree.root_node, source_code, file_path)

        return functions

    def _traverse_ast(self, node: Node, source_code: str, file_path: Path) -> List[FunctionInfo]:
        """
        ASTを再帰的に走査

        Args:
            node: 現在のノード
            source_code: ソースコード全体
            file_path: ファイルパス

        Returns:
            FunctionInfoのリスト
        """
        functions = []

        # 関数定義を検出
        if node.type == 'function_declaration' or node.type == 'method_declaration':
            func_info = self._extract_function_info(node, source_code, file_path)
            if func_info:
                functions.append(func_info)

        # 子ノードを再帰的に走査
        for child in node.children:
            functions.extend(self._traverse_ast(child, source_code, file_path))

        return functions

    def _extract_function_info(self, node: Node, source_code: str, file_path: Path) -> FunctionInfo:
        """
        ノードからFunctionInfoを構築

        Args:
            node: function_declaration or method_declarationノード
            source_code: ソースコード全体
            file_path: ファイルパス

        Returns:
            FunctionInfo
        """
        # 関数名を取得
        name_node = node.child_by_field_name('name')
        function_name = self._get_node_text(name_node, source_code) if name_node else "unknown"

        # コード全体を取得
        code = self._get_node_text(node, source_code)

        # 位置情報
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        start_column = node.start_point[1]
        end_column = node.end_point[1]

        # 引数を抽出
        arguments = self._extract_arguments(node, source_code)

        # docコメントを抽出
        docstring = self._extract_doc_comment(node, source_code)

        # スコープと修飾子を判定
        scope, function_type = self._determine_scope(node)

        # メトリクスを計算
        loc, comment_lines = self._count_lines(code)
        complexity = self._calculate_complexity(code)

        return FunctionInfo(
            name=function_name,
            code=code,
            file_path=str(file_path),
            start_line=start_line,
            end_line=end_line,
            start_column=start_column,
            end_column=end_column,
            language="go",
            function_type=function_type,
            arguments=arguments,
            docstring=docstring,
            scope=scope,
            complexity=complexity,
            loc=loc,
            comment_lines=comment_lines
        )

    def _extract_arguments(self, node: Node, source_code: str) -> List[str]:
        """
        関数の引数を抽出

        Args:
            node: function_declaration or method_declarationノード
            source_code: ソースコード全体

        Returns:
            引数名のリスト
        """
        arguments = []

        # method_declarationの場合、receiverは除外
        parameters_node = node.child_by_field_name('parameters')
        if not parameters_node:
            return arguments

        for child in parameters_node.children:
            # parameter_declaration（通常の引数）
            if child.type == 'parameter_declaration':
                # nameフィールドから引数名を取得
                # Goでは複数の引数が同じ型を持つ場合、カンマ区切りで書ける
                # 例: func Add(a, b int)
                name_nodes = []
                for subchild in child.children:
                    if subchild.type == 'identifier':
                        name_nodes.append(subchild)

                for name_node in name_nodes:
                    arg_name = self._get_node_text(name_node, source_code)
                    arguments.append(arg_name)

        return arguments

    def _extract_doc_comment(self, node: Node, source_code: str) -> str:
        """
        docコメントを抽出

        Goの//コメントはノードの前にあるため、
        前のノードをチェックする

        Args:
            node: function_declaration or method_declarationノード
            source_code: ソースコード全体

        Returns:
            docコメント、または None
        """
        # 親ノードから前のコメントノードを探す
        parent = node.parent
        if not parent:
            return None

        # 関数の直前のコメントを探す
        node_index = None
        for i, child in enumerate(parent.children):
            if child == node:
                node_index = i
                break

        if node_index is None or node_index == 0:
            return None

        # 直前のノードがcommentかチェック
        prev_node = parent.children[node_index - 1]
        if prev_node.type == 'comment':
            comment_text = self._get_node_text(prev_node, source_code)
            # // を除去
            if comment_text.startswith('//'):
                return comment_text[2:].strip()

        return None

    def _determine_scope(self, node: Node) -> tuple[str, str]:
        """
        スコープと関数タイプを判定

        Args:
            node: function_declaration or method_declarationノード

        Returns:
            (scope, function_type) のタプル
        """
        # method_declarationの場合はメソッド
        if node.type == 'method_declaration':
            return "method", "method"

        return "global", "function"

    def _get_node_text(self, node: Node, source_code: str) -> str:
        """
        ノードからテキストを抽出

        Args:
            node: ノード
            source_code: ソースコード全体

        Returns:
            ノードのテキスト
        """
        if node is None:
            return ""

        start_byte = node.start_byte
        end_byte = node.end_byte

        return source_code[start_byte:end_byte]
