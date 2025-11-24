"""
C++パーサー

TDDステップ2-3: Green - テストを通す実装
"""

from pathlib import Path
from typing import List

from tree_sitter import Language, Parser, Node
import tree_sitter_cpp

from src.parser.base_parser import BaseParser, FunctionInfo
from src.utils.logger import get_logger


logger = get_logger(__name__)


class CppParser(BaseParser):
    """C++ファイル用パーサー"""

    def __init__(self):
        """Tree-sitterパーサー初期化"""
        self.language = Language(tree_sitter_cpp.language())
        self.parser = Parser(self.language)

    def get_language(self) -> str:
        """対応言語名を返す"""
        return "cpp"

    def parse_file(self, file_path: Path) -> List[FunctionInfo]:
        """
        C++ファイルを解析

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
        # 関数名を取得
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

        # スコープと関数タイプを判定
        scope, function_type = self._determine_scope(node, function_name, source_code)

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
            language="cpp",
            function_type=function_type,
            arguments=arguments,
            docstring=docstring,
            modifiers=modifiers,
            scope=scope,
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

        # function_declaratorまたはその他のdeclaratorを探す
        return self._get_function_name_from_declarator(declarator, source_code)

    def _get_function_name_from_declarator(self, declarator: Node, source_code: str) -> str:
        """
        declaratorから関数名を抽出

        Args:
            declarator: declaratorノード
            source_code: ソースコード全体

        Returns:
            関数名
        """
        if declarator.type == 'function_declarator':
            # declaratorフィールドから識別子を取得
            inner_declarator = declarator.child_by_field_name('declarator')
            if inner_declarator:
                if inner_declarator.type == 'identifier':
                    return self._get_node_text(inner_declarator, source_code)
                elif inner_declarator.type == 'field_identifier':
                    return self._get_node_text(inner_declarator, source_code)
                elif inner_declarator.type == 'qualified_identifier':
                    # 最後の識別子を取得
                    for child in inner_declarator.children:
                        if child.type == 'identifier':
                            return self._get_node_text(child, source_code)
                else:
                    # 再帰的に探索
                    return self._get_function_name_from_declarator(inner_declarator, source_code)

        elif declarator.type == 'pointer_declarator':
            # pointer_declaratorの中を探す
            inner_declarator = declarator.child_by_field_name('declarator')
            if inner_declarator:
                return self._get_function_name_from_declarator(inner_declarator, source_code)

        elif declarator.type == 'reference_declarator':
            # reference_declaratorの中を探す
            inner_declarator = declarator.child_by_field_name('declarator')
            if inner_declarator:
                return self._get_function_name_from_declarator(inner_declarator, source_code)

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
        function_declarator = self._find_function_declarator(declarator)
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
            elif child.type == 'optional_parameter_declaration':
                # デフォルト引数の場合
                param_declarator = child.child_by_field_name('declarator')
                if param_declarator:
                    arg_name = self._get_identifier_from_declarator(param_declarator, source_code)
                    if arg_name:
                        arguments.append(arg_name)

        return arguments

    def _find_function_declarator(self, declarator: Node) -> Node:
        """
        function_declaratorを見つける

        Args:
            declarator: declaratorノード

        Returns:
            function_declaratorノード、またはNone
        """
        if declarator.type == 'function_declarator':
            return declarator

        # 子ノードを探す
        for child in declarator.named_children:
            result = self._find_function_declarator(child)
            if result:
                return result

        return None

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

        # pointer_declarator、reference_declarator、array_declaratorの場合、内部を探す
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

        C++の/** */コメントはノードの前にあるため、
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

    def _determine_scope(self, node: Node, function_name: str, source_code: str) -> tuple[str, str]:
        """
        スコープと関数タイプを判定

        Args:
            node: function_definitionノード
            function_name: 関数名
            source_code: ソースコード全体

        Returns:
            (scope, function_type) のタプル
        """
        # 親ノードを遡ってclass_specifierを探す
        parent = node.parent
        while parent:
            if parent.type in ['class_specifier', 'struct_specifier']:
                # クラス内のメンバーかチェック
                # コンストラクタかどうか判定（関数名がクラス名と同じ）
                class_name = self._get_class_name(parent, source_code)
                if class_name and class_name == function_name:
                    return "class", "constructor"
                return "class", "method"
            parent = parent.parent

        return "global", "function"

    def _get_class_name(self, class_node: Node, source_code: str = "") -> str:
        """
        クラス名を取得

        Args:
            class_node: class_specifierノード
            source_code: ソースコード全体

        Returns:
            クラス名
        """
        # nameフィールドから取得
        name_node = class_node.child_by_field_name('name')
        if name_node:
            return self._get_node_text(name_node, source_code)

        return None

    def _extract_modifiers(self, node: Node, source_code: str) -> List[str]:
        """
        修飾子を抽出（static, inline, virtual等）

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
            elif child.type == 'virtual_function_specifier':
                modifiers.append('virtual')

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
