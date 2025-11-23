"""
ファイルスキャナーのテスト

TDDステップ1: Red - 失敗するテストを作成
"""

from pathlib import Path

import pytest

from src.scanner.file_scanner import FileScanner, LANGUAGE_EXTENSIONS


class TestFileScanner:
    """FileScannerクラスのテスト"""

    @pytest.fixture
    def sample_project_dir(self):
        """サンプルプロジェクトディレクトリを返す"""
        return Path(__file__).parent / "fixtures" / "sample_project"

    def test_scan_finds_python_files(self, sample_project_dir):
        """Pythonファイルを発見することを確認"""
        scanner = FileScanner(
            source_dir=str(sample_project_dir),
            languages=["python"],
            ignore_file=None  # .ragignoreを無効化
        )
        files = scanner.scan()

        # main.pyとtest_sample.pyが見つかる
        py_files = [f for f in files if f.suffix == ".py"]
        assert len(py_files) >= 1
        assert any("main.py" in str(f) for f in py_files)

    def test_scan_finds_multiple_languages(self, sample_project_dir):
        """複数言語のファイルを発見することを確認"""
        scanner = FileScanner(
            source_dir=str(sample_project_dir),
            languages=["python", "rust", "go"],
            ignore_file=None
        )
        files = scanner.scan()

        # Python, Rust, Goのファイルが見つかる
        assert any(f.suffix == ".py" for f in files)
        assert any(f.suffix == ".rs" for f in files)
        assert any(f.suffix == ".go" for f in files)

    def test_scan_excludes_ignored_files(self, sample_project_dir):
        """ragignoreで除外されたファイルが含まれないことを確認"""
        scanner = FileScanner(
            source_dir=str(sample_project_dir),
            languages=["python"],
            ignore_file=".ragignore"
        )
        files = scanner.scan()

        # test_sample.py（*_test.py）は除外される
        assert not any("test_sample.py" in str(f) for f in files)
        # main.pyは含まれる
        assert any("main.py" in str(f) for f in files)

    def test_scan_excludes_binary_files(self, sample_project_dir):
        """バイナリファイルを除外することを確認"""
        scanner = FileScanner(
            source_dir=str(sample_project_dir),
            languages=None,  # 全言語
            ignore_file=None
        )
        files = scanner.scan()

        # binary.exeは除外される
        assert not any("binary.exe" in str(f) for f in files)

    def test_is_binary_detects_binary(self, sample_project_dir):
        """バイナリ判定が正しいことを確認"""
        scanner = FileScanner(
            source_dir=str(sample_project_dir),
            languages=None,
            ignore_file=None
        )

        binary_file = sample_project_dir / "build" / "binary.exe"
        text_file = sample_project_dir / "src" / "main.py"

        assert scanner._is_binary(binary_file) is True
        assert scanner._is_binary(text_file) is False

    def test_get_language_returns_correct_language(self):
        """言語判定が正しいことを確認"""
        scanner = FileScanner(
            source_dir="/tmp",
            languages=None,
            ignore_file=None
        )

        assert scanner._get_language(Path("test.py")) == "python"
        assert scanner._get_language(Path("test.rs")) == "rust"
        assert scanner._get_language(Path("test.go")) == "go"
        assert scanner._get_language(Path("test.java")) == "java"
        assert scanner._get_language(Path("test.c")) == "c"
        assert scanner._get_language(Path("test.h")) == "c"
        assert scanner._get_language(Path("test.cpp")) == "cpp"
        assert scanner._get_language(Path("test.hpp")) == "cpp"
        assert scanner._get_language(Path("test.txt")) is None

    def test_load_ignore_patterns_parses_ragignore(self, sample_project_dir):
        """ragignoreを正しく解析することを確認"""
        scanner = FileScanner(
            source_dir=str(sample_project_dir),
            languages=None,
            ignore_file=".ragignore"
        )

        # PathSpecが作成されていることを確認
        assert scanner.ignore_spec is not None

    def test_ignore_patterns_match_correctly(self, sample_project_dir):
        """パターンマッチングが正しいことを確認"""
        scanner = FileScanner(
            source_dir=str(sample_project_dir),
            languages=None,
            ignore_file=".ragignore"
        )

        # build/ディレクトリは除外
        assert scanner._is_ignored(Path("build/binary.exe")) is True
        # *.pycは除外
        assert scanner._is_ignored(Path("src/test.pyc")) is True
        # *_test.pyは除外
        assert scanner._is_ignored(Path("src/test_sample.py")) is True
        # 通常のファイルは含まれる
        assert scanner._is_ignored(Path("src/main.py")) is False

    def test_scan_with_specific_languages_only(self, sample_project_dir):
        """特定言語のみをスキャンすることを確認"""
        # Pythonのみ
        scanner = FileScanner(
            source_dir=str(sample_project_dir),
            languages=["python"],
            ignore_file=None
        )
        files = scanner.scan()

        assert all(scanner._get_language(f) == "python" for f in files)
        assert not any(f.suffix == ".rs" for f in files)
        assert not any(f.suffix == ".go" for f in files)


class TestLanguageExtensions:
    """言語拡張子マッピングのテスト"""

    def test_language_extensions_defined(self):
        """LANGUAGE_EXTENSIONSが定義されていることを確認"""
        assert "python" in LANGUAGE_EXTENSIONS
        assert "rust" in LANGUAGE_EXTENSIONS
        assert "go" in LANGUAGE_EXTENSIONS
        assert "java" in LANGUAGE_EXTENSIONS
        assert "c" in LANGUAGE_EXTENSIONS
        assert "cpp" in LANGUAGE_EXTENSIONS

    def test_python_extensions(self):
        """Python拡張子が正しいことを確認"""
        assert ".py" in LANGUAGE_EXTENSIONS["python"]

    def test_c_cpp_extensions(self):
        """C/C++拡張子が正しいことを確認"""
        assert ".c" in LANGUAGE_EXTENSIONS["c"]
        assert ".h" in LANGUAGE_EXTENSIONS["c"]
        assert ".cpp" in LANGUAGE_EXTENSIONS["cpp"]
        assert ".hpp" in LANGUAGE_EXTENSIONS["cpp"]
