"""
Javaパーサーのテスト

TDDステップ2-3: Red - テストを先に書く
"""

import pytest
from pathlib import Path

from src.parser.java_parser import JavaParser


@pytest.fixture
def parser():
    """JavaParserインスタンス"""
    return JavaParser()


@pytest.fixture
def sample_java_file():
    """サンプルJavaファイル"""
    return Path("tests/fixtures/sample_code/Sample.java")


@pytest.fixture
def with_class_file():
    """クラス付きJavaファイル"""
    return Path("tests/fixtures/sample_code/WithClass.java")


@pytest.fixture
def syntax_error_file():
    """構文エラーのあるJavaファイル"""
    return Path("tests/fixtures/sample_code/java_syntax_error.java")


def test_get_language(parser):
    """言語名の取得"""
    assert parser.get_language() == "java"


def test_parse_simple_methods(parser, sample_java_file):
    """シンプルなメソッドの解析"""
    functions = parser.parse_file(sample_java_file)

    assert len(functions) == 3

    # greetメソッド
    greet = functions[0]
    assert greet.name == "greet"
    assert greet.language == "java"
    assert greet.function_type == "method"
    assert greet.scope == "global"
    assert greet.start_line == 8
    assert "greet" in greet.code

    # addメソッド
    add = functions[1]
    assert add.name == "add"
    assert add.function_type == "method"


def test_extract_arguments(parser, sample_java_file):
    """引数の抽出"""
    functions = parser.parse_file(sample_java_file)

    greet = functions[0]
    assert greet.arguments == ["name"]

    add = functions[1]
    assert add.arguments == ["a", "b"]

    no_args = functions[2]
    assert no_args.arguments == []


def test_extract_javadoc(parser, sample_java_file):
    """JavaDocコメントの抽出"""
    functions = parser.parse_file(sample_java_file)

    greet = functions[0]
    assert greet.docstring is not None
    assert "Greet a person" in greet.docstring

    add = functions[1]
    assert add.docstring is not None
    assert "Add two numbers" in add.docstring

    no_args = functions[2]
    assert no_args.docstring is None


def test_parse_class_methods(parser, with_class_file):
    """クラス内メソッドの解析"""
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

    # publicメソッド
    add_method = functions[1]
    assert "public" in add_method.modifiers

    # staticメソッド
    multiply_method = functions[2]
    assert "public" in multiply_method.modifiers
    assert "static" in multiply_method.modifiers

    # privateメソッド
    reset_method = functions[3]
    assert "private" in reset_method.modifiers


def test_syntax_error_handling(parser, syntax_error_file):
    """構文エラーのハンドリング"""
    functions = parser.parse_file(syntax_error_file)
    assert functions == []


def test_file_not_found(parser):
    """存在しないファイル"""
    with pytest.raises(FileNotFoundError):
        parser.parse_file(Path("nonexistent.java"))


def test_position_info(parser, sample_java_file):
    """位置情報の抽出"""
    functions = parser.parse_file(sample_java_file)

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
    assert add_method.language == "java"
    assert isinstance(add_method.code, str)
    assert len(add_method.code) > 0
