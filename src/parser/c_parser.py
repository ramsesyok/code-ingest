"""
Cパーサー

TDDステップ2-3: Green - テストを通す実装
"""

from pathlib import Path
from typing import List

from tree_sitter import Language, Parser, Node
import tree_sitter_c

from src.parser.base_parser import BaseParser, FunctionInfo
from src.utils.logger import get_logger


logger = get_logger(__name__)


class CParser(BaseParser):
    """Cファイル用パーサー"""

    def __init__(self):
        """Tree-sitterパーサー初期化"""
        self.language = Language(tree_sitter_c.language())
        self.parser = Parser(self.language)

    def get_language(self) -> str:
        """対応言語名を返す"""
        return "c"

    def parse_file(self, file_path: Path) -> List[FunctionInfo]:
        """
        Cファイルを解析

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
        if node.type == 'function_definition':
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
            node: function_definitionノード
            source_code: ソースコード全体
            file_path: ファイルパス

        Returns:
            FunctionInfo
        """
        # 関数名を取得（declaratorの中から）
        function_name = self._extract_function_name(node, source_code)

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

        # 修飾子を抽出
        modifiers = self._extract_modifiers(node, source_code)

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
            language="c",
            function_type="function",
            arguments=arguments,
            docstring=docstring,
            modifiers=modifiers,
            scope="global",
            complexity=complexity,
            loc=loc,
            comment_lines=comment_lines
        )

    def _extract_function_name(self, node: Node, source_code: str) -> str:
        """
        関数名を抽出

        Args:
            node: function_definitionノード
            source_code: ソースコード全体

        Returns:
            関数名
        """
        # declaratorノードを探す
        declarator = node.child_by_field_name('declarator')
        if not declarator:
            return "unknown"

        # function_declaratorまたはpointer_declaratorを探す
        while declarator:
            if declarator.type == 'function_declarator':
                # declaratorフィールドから識別子を取得
                inner_declarator = declarator.child_by_field_name('declarator')
                if inner_declarator and inner_declarator.type == 'identifier':
                    return self._get_node_text(inner_declarator, source_code)
                # または直接identifierを探す
                for child in declarator.children:
                    if child.type == 'identifier':
                        return self._get_node_text(child, source_code)
            elif declarator.type == 'pointer_declarator':
                # pointer_declaratorの中を探す
                declarator = declarator.child_by_field_name('declarator')
            else:
                break

        return "unknown"

    def _extract_arguments(self, node: Node, source_code: str) -> List[str]:
        """
        関数の引数を抽出

        Args:
            node: function_definitionノード
            source_code: ソースコード全体

        Returns:
            引数名のリスト
        """
        arguments = []

        # declaratorノードを探す
        declarator = node.child_by_field_name('declarator')
        if not declarator:
            return arguments

        # function_declaratorを探す
        function_declarator = None
        if declarator.type == 'function_declarator':
            function_declarator = declarator
        else:
            # pointer_declaratorの場合、その中を探す
            for child in declarator.named_children:
                if child.type == 'function_declarator':
                    function_declarator = child
                    break

        if not function_declarator:
            return arguments

        # parameter_listを取得
        parameters = function_declarator.child_by_field_name('parameters')
        if not parameters:
            return arguments

        for child in parameters.children:
            if child.type == 'parameter_declaration':
                # declaratorから引数名を取得
                param_declarator = child.child_by_field_name('declarator')
                if param_declarator:
                    arg_name = self._get_identifier_from_declarator(param_declarator, source_code)
                    if arg_name:
                        arguments.append(arg_name)

        return arguments

    def _get_identifier_from_declarator(self, declarator: Node, source_code: str) -> str:
        """
        declaratorから識別子を抽出

        Args:
            declarator: declaratorノード
            source_code: ソースコード全体

        Returns:
            識別子名
        """
        if declarator.type == 'identifier':
            return self._get_node_text(declarator, source_code)

        # pointer_declaratorやarray_declaratorの場合、内部を探す
        for child in declarator.named_children:
            if child.type == 'identifier':
                return self._get_node_text(child, source_code)
            result = self._get_identifier_from_declarator(child, source_code)
            if result:
                return result

        return None

    def _extract_doc_comment(self, node: Node, source_code: str) -> str:
        """
        docコメントを抽出

        Cの/** */コメントはノードの前にあるため、
        前のノードをチェックする

        Args:
            node: function_definitionノード
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
            # /** */ を除去
            if comment_text.startswith('/**'):
                lines = comment_text[3:-2].split('\n')
                cleaned_lines = []
                for line in lines:
                    line = line.strip()
                    if line.startswith('*'):
                        line = line[1:].strip()
                    if line:
                        cleaned_lines.append(line)
                return ' '.join(cleaned_lines) if cleaned_lines else None

        return None

    def _extract_modifiers(self, node: Node, source_code: str) -> List[str]:
        """
        修飾子を抽出（static, inline等）

        Args:
            node: function_definitionノード
            source_code: ソースコード全体

        Returns:
            修飾子のリスト
        """
        modifiers = []

        # storage_class_specifierやtype_qualifierをチェック
        for child in node.children:
            if child.type == 'storage_class_specifier':
                modifier_text = self._get_node_text(child, source_code)
                if modifier_text in ['static', 'extern', 'inline']:
                    modifiers.append(modifier_text)

        return modifiers

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
