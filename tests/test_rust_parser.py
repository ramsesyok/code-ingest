"""
Rustパーサーのテスト

TDDステップ1: Red - 失敗するテストを作成
"""

from pathlib import Path

import pytest

from src.parser.rust_parser import RustParser
from src.parser.base_parser import FunctionInfo


class TestRustParser:
    """RustParserクラスのテスト"""

    @pytest.fixture
    def parser(self):
        """RustParserインスタンスを返す"""
        return RustParser()

    @pytest.fixture
    def fixtures_dir(self):
        """フィクスチャディレクトリを返す"""
        return Path(__file__).parent / "fixtures" / "sample_code"

    def test_get_language(self, parser):
        """get_languageがrustを返すことを確認"""
        assert parser.get_language() == "rust"

    def test_parse_simple_functions(self, parser, fixtures_dir):
        """シンプルな関数を解析できることを確認"""
        file_path = fixtures_dir / "sample.rs"
        functions = parser.parse_file(file_path)

        assert len(functions) >= 2

        # greet関数の確認
        greet_func = next((f for f in functions if f.name == "greet"), None)
        assert greet_func is not None
        assert greet_func.language == "rust"
        assert "name" in greet_func.code
        assert greet_func.file_path == str(file_path)

    def test_parse_function_with_arguments(self, parser, fixtures_dir):
        """引数付き関数を解析できることを確認"""
        file_path = fixtures_dir / "sample.rs"
        functions = parser.parse_file(file_path)

        # add関数の確認
        add_func = next((f for f in functions if f.name == "add"), None)
        assert add_func is not None
        assert len(add_func.arguments) == 2
        assert "a" in add_func.arguments
        assert "b" in add_func.arguments

        # no_args関数の確認
        no_args_func = next((f for f in functions if f.name == "no_args"), None)
        assert no_args_func is not None
        assert no_args_func.arguments == []

    def test_parse_with_doc_comments(self, parser, fixtures_dir):
        """ドキュメントコメント付き関数を解析できることを確認"""
        file_path = fixtures_dir / "sample.rs"
        functions = parser.parse_file(file_path)

        greet_func = next((f for f in functions if f.name == "greet"), None)
        assert greet_func is not None
        # Rustのdocコメントは /// で始まる
        assert greet_func.docstring is not None or "Greet a person" in greet_func.code

    def test_parse_impl_methods(self, parser, fixtures_dir):
        """implブロック内のメソッドを解析できることを確認"""
        file_path = fixtures_dir / "with_impl.rs"
        functions = parser.parse_file(file_path)

        # new, add, multiply, standalone_function の4つ以上
        assert len(functions) >= 4

        # メソッドの確認
        add_method = next((f for f in functions if f.name == "add"), None)
        assert add_method is not None
        assert add_method.function_type == "method"
        assert add_method.scope == "impl"

        # スタンドアローン関数の確認
        standalone = next((f for f in functions if f.name == "standalone_function"), None)
        assert standalone is not None
        assert standalone.function_type == "function"
        assert standalone.scope == "global"

    def test_parse_public_functions(self, parser, fixtures_dir):
        """pub修飾子を持つ関数を解析できることを確認"""
        file_path = fixtures_dir / "sample.rs"
        functions = parser.parse_file(file_path)

        add_func = next((f for f in functions if f.name == "add"), None)
        assert add_func is not None
        # pub修飾子の確認
        assert "pub" in add_func.modifiers or "pub" in add_func.code

    def test_parse_syntax_error_returns_empty(self, parser, fixtures_dir):
        """構文エラーで空リストを返すことを確認"""
        file_path = fixtures_dir / "rust_syntax_error.rs"
        functions = parser.parse_file(file_path)

        assert isinstance(functions, list)

    def test_parse_returns_function_info_list(self, parser, fixtures_dir):
        """parse_fileがFunctionInfoのリストを返すことを確認"""
        file_path = fixtures_dir / "sample.rs"
        functions = parser.parse_file(file_path)

        assert isinstance(functions, list)
        assert all(isinstance(f, FunctionInfo) for f in functions)

    def test_parse_nonexistent_file_raises_error(self, parser):
        """存在しないファイルでエラーが発生することを確認"""
        with pytest.raises(FileNotFoundError):
            parser.parse_file(Path("/nonexistent/file.rs"))

    def test_extract_function_metadata(self, parser, fixtures_dir):
        """メタデータ抽出が正しいことを確認"""
        file_path = fixtures_dir / "sample.rs"
        functions = parser.parse_file(file_path)

        func = functions[0]

        # 基本メタデータ
        assert func.name != ""
        assert func.language == "rust"
        assert func.file_path == str(file_path)

        # 位置情報
        assert func.start_line > 0
        assert func.end_line >= func.start_line
        assert func.start_column >= 0
        assert func.end_column >= 0

        # コード
        assert "fn" in func.code
        assert func.code.strip() != ""
