"""
Cパーサーのテスト

TDDステップ2-3: Red - テストを先に書く
"""

import pytest
from pathlib import Path

from src.parser.c_parser import CParser


@pytest.fixture
def parser():
    """CParserインスタンス"""
    return CParser()


@pytest.fixture
def sample_c_file():
    """サンプルCファイル"""
    return Path("tests/fixtures/sample_code/sample.c")


@pytest.fixture
def with_struct_file():
    """構造体付きCファイル"""
    return Path("tests/fixtures/sample_code/with_struct.c")


@pytest.fixture
def syntax_error_file():
    """構文エラーのあるCファイル"""
    return Path("tests/fixtures/sample_code/c_syntax_error.c")


def test_get_language(parser):
    """言語名の取得"""
    assert parser.get_language() == "c"


def test_parse_simple_functions(parser, sample_c_file):
    """シンプルな関数の解析"""
    functions = parser.parse_file(sample_c_file)

    assert len(functions) == 3

    # greet関数
    greet = functions[0]
    assert greet.name == "greet"
    assert greet.language == "c"
    assert greet.function_type == "function"
    assert greet.scope == "global"
    assert greet.start_line == 8
    assert "greet" in greet.code

    # add関数
    add = functions[1]
    assert add.name == "add"
    assert add.function_type == "function"


def test_extract_arguments(parser, sample_c_file):
    """引数の抽出"""
    functions = parser.parse_file(sample_c_file)

    greet = functions[0]
    assert greet.arguments == ["name"]

    add = functions[1]
    assert add.arguments == ["a", "b"]

    no_args = functions[2]
    assert no_args.arguments == []


def test_extract_doc_comment(parser, sample_c_file):
    """docコメントの抽出"""
    functions = parser.parse_file(sample_c_file)

    greet = functions[0]
    assert greet.docstring is not None
    assert "Greet a person" in greet.docstring

    add = functions[1]
    assert add.docstring is not None
    assert "Add two numbers" in add.docstring

    no_args = functions[2]
    assert no_args.docstring is None


def test_parse_struct_functions(parser, with_struct_file):
    """構造体関連関数の解析"""
    functions = parser.parse_file(with_struct_file)

    # create_calculator, calculator_add, multiply, reset
    assert len(functions) == 4

    create = functions[0]
    assert create.name == "create_calculator"
    assert create.function_type == "function"

    calc_add = functions[1]
    assert calc_add.name == "calculator_add"
    assert calc_add.arguments == ["calc", "x", "y"]


def test_extract_modifiers(parser, with_struct_file):
    """修飾子の抽出"""
    functions = parser.parse_file(with_struct_file)

    # static関数
    multiply = functions[2]
    assert multiply.name == "multiply"
    assert "static" in multiply.modifiers


def test_syntax_error_handling(parser, syntax_error_file):
    """構文エラーのハンドリング"""
    functions = parser.parse_file(syntax_error_file)
    assert functions == []


def test_file_not_found(parser):
    """存在しないファイル"""
    with pytest.raises(FileNotFoundError):
        parser.parse_file(Path("nonexistent.c"))


def test_position_info(parser, sample_c_file):
    """位置情報の抽出"""
    functions = parser.parse_file(sample_c_file)

    greet = functions[0]
    assert greet.start_line > 0
    assert greet.end_line > greet.start_line
    assert greet.start_column >= 0
    assert greet.end_column >= 0


def test_metrics(parser, with_struct_file):
    """メトリクスの計算"""
    functions = parser.parse_file(with_struct_file)

    calc_add = functions[1]
    assert calc_add.loc > 0
    assert calc_add.complexity is not None
    assert calc_add.complexity >= 1


def test_metadata_extraction(parser, with_struct_file):
    """メタデータの抽出"""
    functions = parser.parse_file(with_struct_file)

    calc_add = functions[1]
    assert calc_add.file_path == str(with_struct_file)
    assert calc_add.language == "c"
    assert isinstance(calc_add.code, str)
    assert len(calc_add.code) > 0
