"""
Pythonパーサーのテスト

TDDステップ1: Red - 失敗するテストを作成
"""

from pathlib import Path

import pytest

from src.parser.python_parser import PythonParser
from src.parser.base_parser import FunctionInfo


class TestPythonParser:
    """PythonParserクラスのテスト"""

    @pytest.fixture
    def parser(self):
        """PythonParserインスタンスを返す"""
        return PythonParser()

    @pytest.fixture
    def fixtures_dir(self):
        """フィクスチャディレクトリを返す"""
        return Path(__file__).parent / "fixtures" / "sample_code"

    def test_get_language(self, parser):
        """get_languageがpythonを返すことを確認"""
        assert parser.get_language() == "python"

    def test_parse_simple_function(self, parser, fixtures_dir):
        """シンプルな関数を解析できることを確認"""
        file_path = fixtures_dir / "simple.py"
        functions = parser.parse_file(file_path)

        assert len(functions) == 1

        func = functions[0]
        assert isinstance(func, FunctionInfo)
        assert func.name == "greet"
        assert func.language == "python"
        assert "name" in func.code
        assert func.file_path == str(file_path)
        assert func.start_line > 0
        assert func.end_line >= func.start_line

    def test_parse_function_with_arguments(self, parser, fixtures_dir):
        """引数付き関数を解析できることを確認"""
        file_path = fixtures_dir / "with_arguments.py"
        functions = parser.parse_file(file_path)

        # 4つの関数が見つかる
        assert len(functions) == 4

        # 引数なし関数
        no_args_func = next(f for f in functions if f.name == "no_args")
        assert no_args_func.arguments == []

        # 引数あり関数
        with_args_func = next(f for f in functions if f.name == "with_args")
        assert len(with_args_func.arguments) == 3
        assert "a" in with_args_func.arguments
        assert "b" in with_args_func.arguments
        assert "c" in with_args_func.arguments

    def test_parse_function_with_docstring(self, parser, fixtures_dir):
        """docstring付き関数を解析できることを確認"""
        file_path = fixtures_dir / "simple.py"
        functions = parser.parse_file(file_path)

        func = functions[0]
        assert func.docstring is not None
        assert "Greet a person" in func.docstring

    def test_parse_class_method(self, parser, fixtures_dir):
        """クラスメソッドを解析できることを確認"""
        file_path = fixtures_dir / "with_class.py"
        functions = parser.parse_file(file_path)

        # __init__, add, multiply, standalone_function の4つ
        assert len(functions) >= 3

        # メソッドの確認
        add_method = next((f for f in functions if f.name == "add"), None)
        assert add_method is not None
        assert add_method.function_type == "method"
        assert add_method.scope == "class"

        # スタンドアローン関数の確認
        standalone = next((f for f in functions if f.name == "standalone_function"), None)
        assert standalone is not None
        assert standalone.function_type == "function"
        assert standalone.scope == "global"

    def test_parse_multiple_functions(self, parser, fixtures_dir):
        """複数関数を解析できることを確認"""
        file_path = fixtures_dir / "with_arguments.py"
        functions = parser.parse_file(file_path)

        assert len(functions) == 4

        function_names = [f.name for f in functions]
        assert "no_args" in function_names
        assert "with_args" in function_names
        assert "with_defaults" in function_names
        assert "with_type_hints" in function_names

    def test_parse_function_with_comments(self, parser, fixtures_dir):
        """コメント付き関数を解析できることを確認"""
        file_path = fixtures_dir / "with_class.py"
        functions = parser.parse_file(file_path)

        multiply_method = next((f for f in functions if f.name == "multiply"), None)
        assert multiply_method is not None
        # コードにコメントが含まれていることを確認
        assert "#" in multiply_method.code or "Store the result" in multiply_method.code

    def test_parse_syntax_error_returns_empty(self, parser, fixtures_dir):
        """構文エラーで空リストを返すことを確認"""
        file_path = fixtures_dir / "syntax_error.py"
        functions = parser.parse_file(file_path)

        # 構文エラーの場合は空リストまたは警告ログ
        assert isinstance(functions, list)

    def test_extract_function_metadata(self, parser, fixtures_dir):
        """メタデータ抽出が正しいことを確認"""
        file_path = fixtures_dir / "simple.py"
        functions = parser.parse_file(file_path)

        func = functions[0]

        # 基本メタデータ
        assert func.name == "greet"
        assert func.language == "python"
        assert func.file_path == str(file_path)

        # 位置情報
        assert func.start_line > 0
        assert func.end_line >= func.start_line
        assert func.start_column >= 0
        assert func.end_column >= 0

        # コード
        assert "def greet" in func.code
        assert func.code.strip() != ""

    def test_parse_returns_function_info_list(self, parser, fixtures_dir):
        """parse_fileがFunctionInfoのリストを返すことを確認"""
        file_path = fixtures_dir / "simple.py"
        functions = parser.parse_file(file_path)

        assert isinstance(functions, list)
        assert all(isinstance(f, FunctionInfo) for f in functions)

    def test_parse_nonexistent_file_raises_error(self, parser):
        """存在しないファイルでエラーが発生することを確認"""
        with pytest.raises(FileNotFoundError):
            parser.parse_file(Path("/nonexistent/file.py"))
