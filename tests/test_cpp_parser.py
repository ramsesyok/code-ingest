"""
C++パーサーのテスト

TDDステップ2-3: Red - テストを先に書く
"""

import pytest
from pathlib import Path

from src.parser.cpp_parser import CppParser


@pytest.fixture
def parser():
    """CppParserインスタンス"""
    return CppParser()


@pytest.fixture
def sample_cpp_file():
    """サンプルC++ファイル"""
    return Path("tests/fixtures/sample_code/sample.cpp")


@pytest.fixture
def with_class_file():
    """クラス付きC++ファイル"""
    return Path("tests/fixtures/sample_code/with_class.cpp")


@pytest.fixture
def syntax_error_file():
    """構文エラーのあるC++ファイル"""
    return Path("tests/fixtures/sample_code/cpp_syntax_error.cpp")


def test_get_language(parser):
    """言語名の取得"""
    assert parser.get_language() == "cpp"


def test_parse_simple_functions(parser, sample_cpp_file):
    """シンプルな関数の解析"""
    functions = parser.parse_file(sample_cpp_file)

    assert len(functions) == 3

    # greet関数
    greet = functions[0]
    assert greet.name == "greet"
    assert greet.language == "cpp"
    assert greet.function_type == "function"
    assert greet.scope == "global"
    assert greet.start_line == 9
    assert "greet" in greet.code

    # add関数
    add = functions[1]
    assert add.name == "add"
    assert add.function_type == "function"


def test_extract_arguments(parser, sample_cpp_file):
    """引数の抽出"""
    functions = parser.parse_file(sample_cpp_file)

    greet = functions[0]
    assert greet.arguments == ["name"]

    add = functions[1]
    assert add.arguments == ["a", "b"]

    no_args = functions[2]
    assert no_args.arguments == []


def test_extract_doc_comment(parser, sample_cpp_file):
    """docコメントの抽出"""
    functions = parser.parse_file(sample_cpp_file)

    greet = functions[0]
    assert greet.docstring is not None
    assert "Greet a person" in greet.docstring

    add = functions[1]
    assert add.docstring is not None
    assert "Add two numbers" in add.docstring

    no_args = functions[2]
    assert no_args.docstring is None


def test_parse_class_methods(parser, with_class_file):
    """クラスメソッドの解析"""
    functions = parser.parse_file(with_class_file)

    # Constructor, add, multiply, reset, standaloneFunction
    assert len(functions) == 5

    # コンストラクタ
    constructor = functions[0]
    assert constructor.name == "Calculator"
    assert constructor.function_type == "constructor"
    assert constructor.scope == "class"

    # 通常のメソッド
    add_method = functions[1]
    assert add_method.name == "add"
    assert add_method.function_type == "method"
    assert add_method.scope == "class"
    assert add_method.arguments == ["x", "y"]

    # staticメソッド
    multiply_method = functions[2]
    assert multiply_method.name == "multiply"
    assert multiply_method.function_type == "method"
    assert "static" in multiply_method.modifiers


def test_extract_modifiers(parser, with_class_file):
    """修飾子の抽出"""
    functions = parser.parse_file(with_class_file)

    # staticメソッド
    multiply_method = functions[2]
    assert "static" in multiply_method.modifiers


def test_syntax_error_handling(parser, syntax_error_file):
    """構文エラーのハンドリング"""
    functions = parser.parse_file(syntax_error_file)
    assert functions == []


def test_file_not_found(parser):
    """存在しないファイル"""
    with pytest.raises(FileNotFoundError):
        parser.parse_file(Path("nonexistent.cpp"))


def test_position_info(parser, sample_cpp_file):
    """位置情報の抽出"""
    functions = parser.parse_file(sample_cpp_file)

    greet = functions[0]
    assert greet.start_line > 0
    assert greet.end_line > greet.start_line
    assert greet.start_column >= 0
    assert greet.end_column >= 0


def test_metrics(parser, with_class_file):
    """メトリクスの計算"""
    functions = parser.parse_file(with_class_file)

    add_method = functions[1]
    assert add_method.loc > 0
    assert add_method.complexity is not None
    assert add_method.complexity >= 1


def test_metadata_extraction(parser, with_class_file):
    """メタデータの抽出"""
    functions = parser.parse_file(with_class_file)

    add_method = functions[1]
    assert add_method.file_path == str(with_class_file)
    assert add_method.language == "cpp"
    assert isinstance(add_method.code, str)
    assert len(add_method.code) > 0
