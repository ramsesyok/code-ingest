"""
Goパーサーのテスト

TDDステップ2-3: Red - テストを先に書く
"""

import pytest
from pathlib import Path

from src.parser.go_parser import GoParser


@pytest.fixture
def parser():
    """GoParserインスタンス"""
    return GoParser()


@pytest.fixture
def sample_go_file():
    """サンプルGoファイル"""
    return Path("tests/fixtures/sample_code/sample.go")


@pytest.fixture
def with_methods_file():
    """メソッド付きGoファイル"""
    return Path("tests/fixtures/sample_code/with_methods.go")


@pytest.fixture
def syntax_error_file():
    """構文エラーのあるGoファイル"""
    return Path("tests/fixtures/sample_code/go_syntax_error.go")


def test_get_language(parser):
    """言語名の取得"""
    assert parser.get_language() == "go"


def test_parse_simple_functions(parser, sample_go_file):
    """シンプルな関数の解析"""
    functions = parser.parse_file(sample_go_file)

    assert len(functions) == 3

    # Greet関数
    greet = functions[0]
    assert greet.name == "Greet"
    assert greet.language == "go"
    assert greet.function_type == "function"
    assert greet.scope == "global"
    assert greet.start_line == 8
    assert "Greet" in greet.code

    # Add関数
    add = functions[1]
    assert add.name == "Add"
    assert add.function_type == "function"


def test_extract_arguments(parser, sample_go_file):
    """引数の抽出"""
    functions = parser.parse_file(sample_go_file)

    greet = functions[0]
    assert greet.arguments == ["name"]

    add = functions[1]
    assert add.arguments == ["a", "b"]

    no_args = functions[2]
    assert no_args.arguments == []


def test_extract_doc_comment(parser, sample_go_file):
    """docコメントの抽出"""
    functions = parser.parse_file(sample_go_file)

    greet = functions[0]
    assert greet.docstring == "Greet greets a person by name"

    add = functions[1]
    assert add.docstring == "Add adds two numbers"

    no_args = functions[2]
    assert no_args.docstring is None


def test_parse_methods(parser, with_methods_file):
    """メソッドの解析"""
    functions = parser.parse_file(with_methods_file)

    # NewCalculator, Add, Multiply, StandaloneFunction
    assert len(functions) == 4

    # 通常の関数
    new_calc = functions[0]
    assert new_calc.name == "NewCalculator"
    assert new_calc.function_type == "function"
    assert new_calc.scope == "global"

    # メソッド (receiver付き)
    add_method = functions[1]
    assert add_method.name == "Add"
    assert add_method.function_type == "method"
    assert add_method.scope == "method"
    assert "c" not in add_method.arguments  # receiverは除外
    assert add_method.arguments == ["x", "y"]

    multiply_method = functions[2]
    assert multiply_method.name == "Multiply"
    assert multiply_method.function_type == "method"


def test_syntax_error_handling(parser, syntax_error_file):
    """構文エラーのハンドリング"""
    functions = parser.parse_file(syntax_error_file)
    assert functions == []


def test_file_not_found(parser):
    """存在しないファイル"""
    with pytest.raises(FileNotFoundError):
        parser.parse_file(Path("nonexistent.go"))


def test_position_info(parser, sample_go_file):
    """位置情報の抽出"""
    functions = parser.parse_file(sample_go_file)

    greet = functions[0]
    assert greet.start_line > 0
    assert greet.end_line > greet.start_line
    assert greet.start_column >= 0
    assert greet.end_column >= 0


def test_metrics(parser, with_methods_file):
    """メトリクスの計算"""
    functions = parser.parse_file(with_methods_file)

    add_method = functions[1]
    assert add_method.loc > 0
    assert add_method.complexity is not None
    assert add_method.complexity >= 1


def test_metadata_extraction(parser, with_methods_file):
    """メタデータの抽出"""
    functions = parser.parse_file(with_methods_file)

    add_method = functions[1]
    assert add_method.file_path == str(with_methods_file)
    assert add_method.language == "go"
    assert isinstance(add_method.code, str)
    assert len(add_method.code) > 0
