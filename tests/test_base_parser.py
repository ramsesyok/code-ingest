"""
基底パーサークラスとFunctionInfoのテスト

TDDステップ1: Red - 失敗するテストを作成
"""

from pathlib import Path

import pytest

from src.parser.base_parser import BaseParser, FunctionInfo


class TestFunctionInfo:
    """FunctionInfoデータクラスのテスト"""

    def test_function_info_creation(self):
        """FunctionInfoが作成できることを確認"""
        func_info = FunctionInfo(
            name="test_function",
            code="def test_function():\n    pass",
            file_path="/path/to/file.py",
            start_line=10,
            end_line=11,
            start_column=0,
            end_column=8,
            language="python"
        )

        assert func_info.name == "test_function"
        assert func_info.code == "def test_function():\n    pass"
        assert func_info.file_path == "/path/to/file.py"
        assert func_info.start_line == 10
        assert func_info.end_line == 11
        assert func_info.language == "python"

    def test_function_info_with_defaults(self):
        """デフォルト値が正しく設定されることを確認"""
        func_info = FunctionInfo(
            name="simple",
            code="code",
            file_path="/test.py",
            start_line=1,
            end_line=2,
            start_column=0,
            end_column=4,
            language="python"
        )

        # デフォルト値の確認
        assert func_info.function_type == "function"
        assert func_info.arguments == []
        assert func_info.return_type is None
        assert func_info.docstring is None
        assert func_info.comments == []
        assert func_info.modifiers == []
        assert func_info.scope == "global"
        assert func_info.imports == []
        assert func_info.calls == []
        assert func_info.complexity is None
        assert func_info.loc == 0
        assert func_info.comment_lines == 0

    def test_function_info_with_all_fields(self):
        """全フィールド指定でFunctionInfoを作成できることを確認"""
        func_info = FunctionInfo(
            name="calculate",
            code="def calculate(x, y):\n    return x + y",
            file_path="/calc.py",
            start_line=5,
            end_line=6,
            start_column=0,
            end_column=20,
            language="python",
            function_type="method",
            arguments=["x", "y"],
            return_type="int",
            docstring="Calculate sum",
            comments=["# Helper function"],
            modifiers=["public"],
            scope="class",
            imports=["math"],
            calls=["add"],
            complexity=2,
            loc=2,
            comment_lines=1
        )

        assert func_info.name == "calculate"
        assert func_info.function_type == "method"
        assert func_info.arguments == ["x", "y"]
        assert func_info.return_type == "int"
        assert func_info.docstring == "Calculate sum"
        assert func_info.comments == ["# Helper function"]
        assert func_info.modifiers == ["public"]
        assert func_info.scope == "class"
        assert func_info.imports == ["math"]
        assert func_info.calls == ["add"]
        assert func_info.complexity == 2
        assert func_info.loc == 2
        assert func_info.comment_lines == 1


class TestBaseParser:
    """BaseParserクラスのテスト"""

    def test_base_parser_is_abstract(self):
        """BaseParserが抽象クラスであることを確認"""
        with pytest.raises(TypeError):
            # 抽象クラスは直接インスタンス化できない
            BaseParser()

    def test_base_parser_parse_file_is_abstract(self):
        """parse_fileが抽象メソッドであることを確認"""
        # 抽象メソッドを実装していないサブクラスはインスタンス化できない
        class IncompleteParser(BaseParser):
            def get_language(self):
                return "test"

        with pytest.raises(TypeError):
            IncompleteParser()

    def test_base_parser_get_language_is_abstract(self):
        """get_languageが抽象メソッドであることを確認"""
        # 抽象メソッドを実装していないサブクラスはインスタンス化できない
        class IncompleteParser(BaseParser):
            def parse_file(self, file_path):
                return []

        with pytest.raises(TypeError):
            IncompleteParser()

    def test_concrete_parser_can_be_instantiated(self):
        """抽象メソッドを実装したサブクラスはインスタンス化できることを確認"""
        class ConcreteParser(BaseParser):
            def parse_file(self, file_path):
                return []

            def get_language(self):
                return "test"

        # 全ての抽象メソッドを実装していればインスタンス化できる
        parser = ConcreteParser()
        assert parser.get_language() == "test"
        assert parser.parse_file(Path("/test.py")) == []

    def test_count_lines_utility(self):
        """_count_linesユーティリティメソッドが正しく動作することを確認"""
        class ConcreteParser(BaseParser):
            def parse_file(self, file_path):
                return []

            def get_language(self):
                return "test"

        parser = ConcreteParser()

        code = """def hello():
    # This is a comment
    print("Hello")

    # Another comment
    return True
"""
        loc, comment_lines = parser._count_lines(code)

        # 実効行数: 3行 (def, print, return)
        # コメント行数: 2行
        assert loc == 3
        assert comment_lines == 2

    def test_calculate_complexity_utility(self):
        """_calculate_complexityユーティリティメソッドが正しく動作することを確認"""
        class ConcreteParser(BaseParser):
            def parse_file(self, file_path):
                return []

            def get_language(self):
                return "test"

        parser = ConcreteParser()

        # 分岐なし: 複雑度 1
        simple_code = "def simple():\n    return 1"
        assert parser._calculate_complexity(simple_code) == 1

        # if文1つ: 複雑度 2
        code_with_if = """def test():
    if x > 0:
        return True
    return False
"""
        assert parser._calculate_complexity(code_with_if) == 2

        # if + for: 複雑度 3
        complex_code = """def complex():
    if x > 0:
        for i in range(10):
            print(i)
"""
        assert parser._calculate_complexity(complex_code) == 3
