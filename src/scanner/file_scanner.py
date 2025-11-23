"""
ファイルスキャナー

TDDステップ4: Refactor - コードの改善
"""

from pathlib import Path
from typing import List, Optional

import pathspec


# 言語別拡張子マッピング
LANGUAGE_EXTENSIONS = {
    'python': ['.py'],
    'rust': ['.rs'],
    'go': ['.go'],
    'java': ['.java'],
    'c': ['.c', '.h'],
    'cpp': ['.cpp', '.cc', '.cxx', '.hpp', '.hh', '.hxx']
}


class FileScanner:
    """ファイルスキャン・除外処理を行うクラス"""

    def __init__(
        self,
        source_dir: str,
        languages: Optional[List[str]] = None,
        ignore_file: Optional[str] = None
    ):
        """
        初期化

        Args:
            source_dir: スキャン対象ディレクトリ
            languages: 対象言語リスト（Noneの場合は全言語）
            ignore_file: .ragignoreファイル名（Noneの場合は除外なし）
        """
        self.source_dir = Path(source_dir)
        self.languages = languages
        self.ignore_file = ignore_file
        self.ignore_spec = self._load_ignore_patterns()

    def scan(self) -> List[Path]:
        """
        ファイルをスキャンして対象ファイルリストを返す

        Returns:
            対象ファイルのPathリスト
        """
        files = []

        # source_dirの再帰的走査
        for file_path in self.source_dir.rglob('*'):
            # ディレクトリはスキップ
            if not file_path.is_file():
                continue

            # 相対パスを取得（.ragignore用）
            try:
                relative_path = file_path.relative_to(self.source_dir)
            except ValueError:
                continue

            # .ragignoreパターンマッチング
            if self._is_ignored(relative_path):
                continue

            # バイナリファイル除外
            if self._is_binary(file_path):
                continue

            # 言語判定
            language = self._get_language(file_path)
            if language is None:
                continue

            # 対象言語フィルタリング
            if self.languages is not None and language not in self.languages:
                continue

            files.append(file_path)

        return files

    def _load_ignore_patterns(self) -> Optional[pathspec.PathSpec]:
        """
        .ragignoreを読み込んでPathSpecオブジェクト作成

        Returns:
            PathSpecオブジェクト、または None
        """
        if self.ignore_file is None:
            return None

        ignore_path = self.source_dir / self.ignore_file
        if not ignore_path.exists():
            return None

        with open(ignore_path, 'r', encoding='utf-8') as f:
            patterns = f.read().splitlines()

        # gitignore互換の文法でPathSpecを作成
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)

    def _is_ignored(self, path: Path) -> bool:
        """
        PathSpecによる除外判定

        Args:
            path: チェック対象パス（相対パス）

        Returns:
            True: 除外対象, False: 対象
        """
        if self.ignore_spec is None:
            return False

        # Pathオブジェクトを文字列に変換（POSIX形式）
        path_str = path.as_posix()

        return self.ignore_spec.match_file(path_str)

    def _is_binary(self, path: Path) -> bool:
        """
        バイナリファイル判定

        Args:
            path: チェック対象ファイルパス

        Returns:
            True: バイナリ, False: テキスト
        """
        try:
            with open(path, 'rb') as f:
                chunk = f.read(8192)
                return b'\x00' in chunk
        except Exception:
            # 読み込めない場合はバイナリ扱い
            return True

    def _get_language(self, path: Path) -> Optional[str]:
        """
        ファイルの言語判定

        Args:
            path: ファイルパス

        Returns:
            言語名（python/rust/go/java/c/cpp）、または None
        """
        suffix = path.suffix.lower()

        for language, extensions in LANGUAGE_EXTENSIONS.items():
            if suffix in extensions:
                return language

        return None
