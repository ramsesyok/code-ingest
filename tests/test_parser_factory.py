"""
ParserFactoryのテスト

TDDステップ4-4: Red - テストを先に書く
"""

import pytest
from pathlib import Path

from src.parser.parser_factory import ParserFactory
from src.parser.python_parser import PythonParser
from src.parser.rust_parser import RustParser
from src.parser.go_parser import GoParser
from src.parser.java_parser import JavaParser
from src.parser.c_parser import CParser
from src.parser.cpp_parser import CppParser


@pytest.fixture
def factory():
    """ParserFactoryインスタンス"""
    return ParserFactory()


def test_get_python_parser(factory):
    """Pythonパーサーの取得"""
    parser = factory.get_parser(Path("test.py"))
    assert parser is not None
    assert isinstance(parser, PythonParser)
    assert parser.get_language() == "python"


def test_get_rust_parser(factory):
    """Rustパーサーの取得"""
    parser = factory.get_parser(Path("test.rs"))
    assert parser is not None
    assert isinstance(parser, RustParser)
    assert parser.get_language() == "rust"


def test_get_go_parser(factory):
    """Goパーサーの取得"""
    parser = factory.get_parser(Path("test.go"))
    assert parser is not None
    assert isinstance(parser, GoParser)
    assert parser.get_language() == "go"


def test_get_java_parser(factory):
    """Javaパーサーの取得"""
    parser = factory.get_parser(Path("test.java"))
    assert parser is not None
    assert isinstance(parser, JavaParser)
    assert parser.get_language() == "java"


def test_get_c_parser(factory):
    """Cパーサーの取得"""
    parser = factory.get_parser(Path("test.c"))
    assert parser is not None
    assert isinstance(parser, CParser)
    assert parser.get_language() == "c"

    # .hファイルもCとして扱う
    parser_h = factory.get_parser(Path("test.h"))
    assert parser_h is not None
    assert isinstance(parser_h, CParser)


def test_get_cpp_parser(factory):
    """C++パーサーの取得"""
    # .cpp
    parser_cpp = factory.get_parser(Path("test.cpp"))
    assert parser_cpp is not None
    assert isinstance(parser_cpp, CppParser)
    assert parser_cpp.get_language() == "cpp"

    # .cc
    parser_cc = factory.get_parser(Path("test.cc"))
    assert parser_cc is not None
    assert isinstance(parser_cc, CppParser)

    # .cxx
    parser_cxx = factory.get_parser(Path("test.cxx"))
    assert parser_cxx is not None
    assert isinstance(parser_cxx, CppParser)

    # .hpp
    parser_hpp = factory.get_parser(Path("test.hpp"))
    assert parser_hpp is not None
    assert isinstance(parser_hpp, CppParser)

    # .hh
    parser_hh = factory.get_parser(Path("test.hh"))
    assert parser_hh is not None
    assert isinstance(parser_hh, CppParser)

    # .hxx
    parser_hxx = factory.get_parser(Path("test.hxx"))
    assert parser_hxx is not None
    assert isinstance(parser_hxx, CppParser)


def test_unsupported_extension(factory):
    """未対応の拡張子"""
    parser = factory.get_parser(Path("test.txt"))
    assert parser is None

    parser = factory.get_parser(Path("test.unknown"))
    assert parser is None


def test_case_insensitive_extension(factory):
    """大文字小文字を区別しない"""
    parser_py = factory.get_parser(Path("test.PY"))
    assert parser_py is not None
    assert isinstance(parser_py, PythonParser)

    parser_rs = factory.get_parser(Path("test.RS"))
    assert parser_rs is not None
    assert isinstance(parser_rs, RustParser)


def test_singleton_pattern(factory):
    """シングルトンパターン - 同じパーサーインスタンスを返す"""
    parser1 = factory.get_parser(Path("test1.py"))
    parser2 = factory.get_parser(Path("test2.py"))

    # 同じインスタンスを返すことを確認
    assert parser1 is parser2


def test_lazy_initialization(factory):
    """遅延初期化 - 初回アクセス時に初期化される"""
    # 初期化前は_initializedがFalse
    assert factory._initialized == False

    # get_parserを呼ぶと初期化される
    factory.get_parser(Path("test.py"))
    assert factory._initialized == True

    # 2回目以降は初期化されない（既に初期化済み）
    factory.get_parser(Path("test.rs"))
    assert factory._initialized == True


def test_detect_language(factory):
    """言語判定のテスト"""
    assert factory._detect_language(Path("test.py")) == "python"
    assert factory._detect_language(Path("test.rs")) == "rust"
    assert factory._detect_language(Path("test.go")) == "go"
    assert factory._detect_language(Path("test.java")) == "java"
    assert factory._detect_language(Path("test.c")) == "c"
    assert factory._detect_language(Path("test.h")) == "c"
    assert factory._detect_language(Path("test.cpp")) == "cpp"
    assert factory._detect_language(Path("test.cc")) == "cpp"
    assert factory._detect_language(Path("test.cxx")) == "cpp"
    assert factory._detect_language(Path("test.hpp")) == "cpp"
    assert factory._detect_language(Path("test.hh")) == "cpp"
    assert factory._detect_language(Path("test.hxx")) == "cpp"
    assert factory._detect_language(Path("test.txt")) is None


def test_get_all_supported_languages(factory):
    """全ての対応言語のパーサーを取得できる"""
    factory._initialize_parsers()

    assert "python" in factory._parsers
    assert "rust" in factory._parsers
    assert "go" in factory._parsers
    assert "java" in factory._parsers
    assert "c" in factory._parsers
    assert "cpp" in factory._parsers

    assert len(factory._parsers) == 6
