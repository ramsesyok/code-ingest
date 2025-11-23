# Code RAG Indexer - 基本設計書（Claude Code実装指示書）

**文書バージョン**: 1.1  
**作成日**: 2025-11-23  
**更新日**: 2025-11-23  
**対象**: Claude Code による実装  
**実装言語**: Python 3.11以上  
**開発手法**: テスト駆動開発（TDD）

---

## 1. プロジェクト構造

```
code-ingest/
├── src/
│   ├── __init__.py
│   ├── main.py                 # エントリーポイント
│   ├── config/
│   │   ├── __init__.py
│   │   └── config_loader.py   # 設定ファイル読み込み
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── base_parser.py     # パーサー基底クラス
│   │   ├── python_parser.py   # Python用パーサー
│   │   ├── rust_parser.py     # Rust用パーサー
│   │   ├── go_parser.py       # Go用パーサー
│   │   ├── java_parser.py     # Java用パーサー
│   │   ├── c_parser.py        # C用パーサー
│   │   ├── cpp_parser.py      # C++用パーサー
│   │   └── parser_factory.py  # パーサーファクトリ
│   ├── embedder/
│   │   ├── __init__.py
│   │   └── code_embedder.py   # コード埋め込みモデル
│   ├── indexer/
│   │   ├── __init__.py
│   │   └── qdrant_indexer.py  # Qdrant登録処理
│   ├── scanner/
│   │   ├── __init__.py
│   │   └── file_scanner.py    # ファイルスキャン・除外処理
│   └── utils/
│       ├── __init__.py
│       └── logger.py          # ロギング設定
├── tests/
│   ├── __init__.py
│   ├── fixtures/              # テストデータ
│   │   ├── configs/          # テスト用設定ファイル
│   │   └── sample_code/      # テスト用ソースコード
│   ├── test_logger.py
│   ├── test_config_loader.py
│   ├── test_file_scanner.py
│   ├── test_base_parser.py
│   ├── test_python_parser.py
│   ├── test_rust_parser.py
│   ├── test_go_parser.py
│   ├── test_java_parser.py
│   ├── test_c_parser.py
│   ├── test_cpp_parser.py
│   ├── test_parser_factory.py
│   ├── test_code_embedder.py
│   ├── test_qdrant_indexer.py
│   ├── test_main.py
│   └── test_e2e.py
├── config.yaml.example         # 設定ファイルサンプル
├── .ragignore.example         # .ragignoreサンプル
├── requirements.txt           # Python依存パッケージ
├── pytest.ini                 # pytestの設定
├── Dockerfile
├── docker-compose.yml
├── .gitignore
├── README.md
└── setup.py
```

---

## 2. 環境設定ファイル

### 2.1 requirements.txt

```txt
# テストフレームワーク
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0

# 本体依存
transformers>=4.35.0
torch>=2.2.0
qdrant-client>=1.7.0
tree-sitter>=0.20.0
tree-sitter-python>=0.20.0
tree-sitter-rust>=0.20.0
tree-sitter-go>=0.20.0
tree-sitter-java>=0.20.0
tree-sitter-c>=0.20.0
tree-sitter-cpp>=0.20.0
PyYAML>=6.0
pathspec>=0.11.0
```

### 2.2 pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=src --cov-report=html --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

### 2.3 .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# テスト・カバレッジ
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo

# ログ
*.log

# OS
.DS_Store
Thumbs.db

# プロジェクト固有
qdrant_data/
model_cache/
config.yaml
```

---

## 3. データモデル設計

### 3.1 FunctionInfo - 関数情報データクラス

**ファイル**: `src/parser/base_parser.py`

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class FunctionInfo:
    """関数・メソッドの情報を保持するデータクラス"""
    
    # 基本情報
    name: str                           # 関数名
    code: str                           # コード全体（コメント含む）
    file_path: str                      # ファイルパス
    start_line: int                     # 開始行
    end_line: int                       # 終了行
    start_column: int                   # 開始列
    end_column: int                     # 終了列
    language: str                       # 言語名（python/rust/go/java/c/cpp）
    
    # 構文要素
    function_type: str = "function"     # 関数タイプ（function/method/class）
    arguments: List[str] = field(default_factory=list)  # 引数リスト
    return_type: Optional[str] = None   # 戻り値の型
    
    # ドキュメント
    docstring: Optional[str] = None     # ドキュメント文字列
    comments: List[str] = field(default_factory=list)  # コメント
    
    # 修飾子・スコープ
    modifiers: List[str] = field(default_factory=list)  # 修飾子（public/private/static等）
    scope: str = "global"               # スコープ（global/class/local）
    
    # 依存関係
    imports: List[str] = field(default_factory=list)    # import/include文
    calls: List[str] = field(default_factory=list)      # 呼び出す関数リスト
    
    # メトリクス
    complexity: Optional[int] = None    # サイクロマティック複雑度
    loc: int = 0                        # 実効行数（Lines of Code）
    comment_lines: int = 0              # コメント行数
```

### 3.2 Config - 設定データクラス

**ファイル**: `src/config/config_loader.py`

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import os

@dataclass
class InputConfig:
    """入力設定"""
    source_dir: Path
    ignore_file: str = ".ragignore"

@dataclass
class QdrantConfig:
    """Qdrant設定"""
    url: str
    collection_name: str
    api_key: Optional[str] = None

@dataclass
class EmbeddingConfig:
    """埋め込みモデル設定"""
    model_name: str = "jinaai/jina-embeddings-v2-base-code"
    dimension: int = 768
    max_length: int = 8192
    batch_size: int = 8

@dataclass
class ProcessingConfig:
    """処理設定"""
    parallel_workers: int = field(default_factory=lambda: os.cpu_count() or 4)
    languages: List[str] = field(
        default_factory=lambda: ["python", "rust", "go", "java", "c", "cpp"]
    )

@dataclass
class LoggingConfig:
    """ログ設定"""
    level: str = "INFO"
    file: Optional[str] = "code-ingest.log"

@dataclass
class Config:
    """全体設定"""
    input: InputConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    processing: ProcessingConfig
    logging: LoggingConfig
```

---

## 4. モジュール設計詳細

### 4.1 main.py - エントリーポイント

**責務**: プログラムの起動、全体フロー制御

**主要機能**:
- コマンドライン引数の解析（argparse使用）
- 設定ファイルの読み込み
- ロガーの初期化
- 各処理フェーズの実行
- エラーハンドリングと終了コード返却

**処理フロー**:
```
1. parse_arguments() - 引数解析
   ├─ -c/--config: 設定ファイルパス（必須）
   ├─ -v/--verbose: 詳細ログ
   └─ --version: バージョン表示

2. ConfigLoader.load() - 設定読み込み

3. setup_logger() - ロガー初期化

4. Phase 1: ファイルスキャン
   └─ FileScanner.scan() → List[Path]

5. Phase 2: AST解析
   └─ ParserFactory.get_parser() → Parser
   └─ Parser.parse_file() → List[FunctionInfo]

6. Phase 3: ベクトル化とQdrant登録
   ├─ QdrantIndexer.create_collection()
   ├─ CodeEmbedder.embed_batch() → List[List[float]]
   └─ QdrantIndexer.upsert_batch()

7. サマリー表示

8. 終了（return 0 or 1）
```

**エラーハンドリング**:
| 例外 | 処理 | 終了コード |
|------|------|-----------|
| FileNotFoundError | ERROR終了 | 1 |
| ConnectionError | ERROR終了 | 1 |
| ValueError | ERROR終了 | 1 |
| Exception | ERROR終了（スタックトレース） | 1 |

**ログ出力**:
- 各フェーズの開始・完了
- 処理済みファイル数
- 抽出された関数数
- 登録完了件数

---

### 4.2 utils/logger.py - ロギング

**責務**: 統一的なログ出力設定

**主要機能**:
- ファイル+コンソール同時出力
- レベル別フォーマット
- モジュール別ロガー取得

**ログフォーマット**:
```
[YYYY-MM-DD HH:MM:SS] [LEVEL] [MODULE] MESSAGE
```

**関数**:
```python
def setup_logger(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    ロガーを初期化
    
    Args:
        level: ログレベル（DEBUG/INFO/WARN/ERROR）
        log_file: ログファイルパス（Noneの場合はコンソールのみ）
    
    Returns:
        設定済みロガー
    """

def get_logger(name: str) -> logging.Logger:
    """
    モジュール別ロガーを取得
    
    Args:
        name: モジュール名（通常は __name__）
    
    Returns:
        ロガーインスタンス
    """
```

**実装要件**:
- 標準ライブラリ`logging`を使用
- コンソールハンドラー（常に出力）
- ファイルハンドラー（log_file指定時のみ）
- フォーマッター設定
- ログレベルの動的変更対応

---

### 4.3 config/config_loader.py - 設定ファイル読み込み

**責務**: YAML設定ファイルの読み込み、バリデーション、環境変数展開

**主要メソッド**:

```python
class ConfigLoader:
    @staticmethod
    def load(config_path: Path) -> Config:
        """
        設定ファイルを読み込む
        
        処理:
        1. YAMLファイル読み込み
        2. 環境変数展開（${VAR_NAME}）
        3. デフォルト値適用
        4. データクラス構築
        5. バリデーション
        
        Raises:
            FileNotFoundError: 設定ファイルが存在しない
            ValueError: 設定が不正
        """
    
    @staticmethod
    def _expand_env_vars(obj: Any) -> Any:
        """
        環境変数を再帰的に展開
        
        ${VAR_NAME} 形式を os.environ[VAR_NAME] で置換
        """
    
    @staticmethod
    def _validate(config: Config) -> None:
        """
        設定をバリデーション
        
        チェック項目:
        - source_dirの存在確認
        - Qdrant URLの形式（http/https）
        - ログレベルの妥当性
        """
```

**バリデーション詳細**:
| 項目 | チェック内容 | エラーメッセージ |
|------|------------|----------------|
| source_dir | ディレクトリ存在 | "Source directory does not exist: {path}" |
| qdrant.url | http/https開始 | "Invalid Qdrant URL: {url}" |
| logging.level | 有効なレベル | "Invalid log level: {level}" |
| collection_name | 未指定時 | ディレクトリ名を自動設定 |

**環境変数展開例**:
```yaml
qdrant:
  api_key: "${QDRANT_API_KEY}"  # → os.environ["QDRANT_API_KEY"]
```

---

### 4.4 scanner/file_scanner.py - ファイルスキャン

**責務**: ディレクトリ走査、ファイル除外、バイナリ検出

**言語別拡張子マッピング**:
```python
LANGUAGE_EXTENSIONS = {
    'python': ['.py'],
    'rust': ['.rs'],
    'go': ['.go'],
    'java': ['.java'],
    'c': ['.c', '.h'],
    'cpp': ['.cpp', '.cc', '.cxx', '.hpp', '.hh', '.hxx']
}
```

**主要メソッド**:

```python
class FileScanner:
    def __init__(self, config: Config):
        """初期化・.ragignore読み込み"""
    
    def scan(self) -> List[Path]:
        """
        ファイルをスキャンして対象ファイルリストを返す
        
        処理:
        1. source_dirの再帰的走査（Path.rglob）
        2. 拡張子による言語判定
        3. .ragignoreパターンマッチング
        4. バイナリファイル除外
        5. 対象言語フィルタリング
        
        Returns:
            対象ファイルのPathリスト
        """
    
    def _load_ignore_patterns(self) -> pathspec.PathSpec:
        """
        .ragignoreを読み込んでPathSpecオブジェクト作成
        
        gitignore互換の文法をサポート
        """
    
    def _is_ignored(self, path: Path) -> bool:
        """
        PathSpecによる除外判定
        
        Args:
            path: チェック対象パス（相対パス）
        
        Returns:
            True: 除外対象, False: 対象
        """
    
    def _is_binary(self, path: Path) -> bool:
        """
        バイナリファイル判定
        
        処理:
        - 先頭8192バイト読み込み
        - NULL文字（\\x00）の存在チェック
        
        Returns:
            True: バイナリ, False: テキスト
        """
    
    def _get_language(self, path: Path) -> Optional[str]:
        """
        ファイルの言語判定
        
        拡張子から言語を判定
        """
```

**.ragignore処理**:
- `pathspec`ライブラリを使用
- gitignore互換の文法
- コメント行（#）は無視
- パターン例: `*.pyc`, `__pycache__/`, `build/*`

**バイナリ検出アルゴリズム**:
```python
def _is_binary(self, path: Path) -> bool:
    try:
        with open(path, 'rb') as f:
            chunk = f.read(8192)
            return b'\x00' in chunk
    except Exception:
        return True  # 読み込めない場合はバイナリ扱い
```

---

### 4.5 parser/base_parser.py - パーサー基底クラス

**責務**: 各言語パーサーの共通インターフェース定義

**抽象基底クラス設計**:

```python
from abc import ABC, abstractmethod
from typing import List
from pathlib import Path

class BaseParser(ABC):
    """パーサー基底クラス"""
    
    @abstractmethod
    def parse_file(self, file_path: Path) -> List[FunctionInfo]:
        """
        ファイルを解析して関数情報リストを返す
        
        Args:
            file_path: 解析対象ファイル
        
        Returns:
            FunctionInfoのリスト
        
        Raises:
            SyntaxError: 構文エラー（サブクラスで処理）
        """
        pass
    
    @abstractmethod
    def get_language(self) -> str:
        """
        対応言語名を返す
        
        Returns:
            言語名（python/rust/go/java/c/cpp）
        """
        pass
    
    # 共通ユーティリティメソッド（実装済み）
    
    def _count_lines(self, code: str) -> tuple[int, int]:
        """
        実効行数とコメント行数をカウント
        
        Returns:
            (実効行数, コメント行数)
        """
    
    def _calculate_complexity(self, code: str) -> int:
        """
        サイクロマティック複雑度を計算
        
        簡易実装: 分岐文（if/for/while等）の数 + 1
        """
```

**共通ユーティリティ実装方針**:
- `_count_lines`: 空行、コメント行を除いた行数カウント
- `_calculate_complexity`: 制御構造のカウント（言語依存を最小化）

---

### 4.6 parser/python_parser.py (および他言語パーサー)

**責務**: 言語固有のAST解析

**実装方針**:
- **Tree-sitter**を使用（全言語統一）
- BaseParserを継承
- 言語別Tree-sitter文法を使用

**主要メソッド**:

```python
class PythonParser(BaseParser):
    def __init__(self):
        """Tree-sitterパーサー初期化"""
        self.language = Language(tree_sitter_python.language())
        self.parser = Parser(self.language)
    
    def parse_file(self, file_path: Path) -> List[FunctionInfo]:
        """
        Pythonファイルを解析
        
        処理フロー:
        1. ファイル読み込み（UTF-8）
        2. Tree-sitterでパース
        3. AST走査（_traverse_ast）
        4. FunctionInfoリスト構築
        
        エラーハンドリング:
        - UnicodeDecodeError: WARNING、空リスト返却
        - SyntaxError: WARNING、空リスト返却
        """
    
    def _traverse_ast(self, node, source_code: str, file_path: Path) -> List[FunctionInfo]:
        """
        ASTを再帰的に走査
        
        検出対象ノード:
        - function_definition: 関数定義
        - class_definition: クラス定義
        """
    
    def _extract_function_info(self, node, source_code: str, file_path: Path) -> FunctionInfo:
        """
        ノードからFunctionInfoを構築
        
        抽出情報:
        - 関数名: identifier ノード
        - 引数: parameters ノード
        - docstring: string ノード（最初の文字列リテラル）
        - コメント: comment ノード
        - 本体: block ノード
        """
    
    def _get_node_text(self, node, source_code: str) -> str:
        """ノードからテキスト抽出"""
    
    def get_language(self) -> str:
        return "python"
```

**Tree-sitterノードタイプマッピング**:

| 言語 | 関数定義ノード | クラス定義ノード | 引数ノード |
|------|---------------|-----------------|-----------|
| Python | `function_definition` | `class_definition` | `parameters` |
| Rust | `function_item` | `impl_item` | `parameters` |
| Go | `function_declaration` | `type_declaration` | `parameter_list` |
| Java | `method_declaration` | `class_declaration` | `formal_parameters` |
| C | `function_definition` | N/A | `parameter_list` |
| C++ | `function_definition` | `class_specifier` | `parameter_list` |

**エラーハンドリング**:
```python
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
except UnicodeDecodeError as e:
    logger.warning(f"Encoding error in {file_path}: {e}")
    return []

tree = self.parser.parse(bytes(code, "utf8"))
if tree.root_node.has_error:
    logger.warning(f"Syntax error in {file_path}")
    return []
```

---

### 4.7 parser/parser_factory.py - パーサーファクトリ

**責務**: ファイル拡張子に応じた適切なパーサーの提供

**実装**:

```python
class ParserFactory:
    """パーサーファクトリ（シングルトンパターン）"""
    
    _parsers: Dict[str, BaseParser] = {}
    
    def __init__(self):
        """遅延初期化（get_parserで初回アクセス時に初期化）"""
        self._initialized = False
    
    def _initialize_parsers(self):
        """パーサーインスタンスを初期化"""
        if not self._initialized:
            self._parsers = {
                'python': PythonParser(),
                'rust': RustParser(),
                'go': GoParser(),
                'java': JavaParser(),
                'c': CParser(),
                'cpp': CppParser()
            }
            self._initialized = True
    
    def get_parser(self, file_path: Path) -> Optional[BaseParser]:
        """
        ファイルパスからパーサーを取得
        
        Args:
            file_path: ソースファイルパス
        
        Returns:
            対応するパーサー、未対応の場合None
        """
        self._initialize_parsers()
        language = self._detect_language(file_path)
        return self._parsers.get(language)
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """
        拡張子から言語を判定
        
        Returns:
            言語名（python/rust/go/java/c/cpp）
        """
        suffix = file_path.suffix.lower()
        
        extension_map = {
            '.py': 'python',
            '.rs': 'rust',
            '.go': 'go',
            '.java': 'java',
            '.c': 'c',
            '.h': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.hpp': 'cpp',
            '.hh': 'cpp',
            '.hxx': 'cpp'
        }
        
        return extension_map.get(suffix)
```

**シングルトンパターン**:
- 各パーサーインスタンスを1つだけ保持
- Tree-sitterの初期化コストを削減
- スレッドセーフは不要（シングルスレッド前提）

---

### 4.8 embedder/code_embedder.py - コード埋め込み

**責務**: コードをベクトルに変換

**主要メソッド**:

```python
class CodeEmbedder:
    def __init__(self, config: Config):
        """
        埋め込みモデルの初期化
        
        処理:
        1. transformersからモデル・トークナイザー読み込み
        2. GPU/CPU自動検出
        3. モデルをデバイスに転送
        
        設定:
        - model_name: jinaai/jina-embeddings-v2-base-code
        - trust_remote_code: True（Jinaモデルに必要）
        """
        logger.info(f"Loading embedding model: {config.embedding.model_name}")
        
        self.model = AutoModel.from_pretrained(
            config.embedding.model_name,
            trust_remote_code=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.embedding.model_name,
            trust_remote_code=True
        )
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()  # 推論モード
        
        self.max_length = config.embedding.max_length
        
        logger.info(f"Model loaded on device: {self.device}")
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        バッチでコードをベクトル化
        
        Args:
            texts: コードテキストのリスト
        
        Returns:
            768次元ベクトルのリスト
        
        処理:
        1. トークナイズ（max_length, truncation, padding）
        2. モデルに入力
        3. 最終隠れ層の平均プーリング
        4. CPUに転送してリスト化
        """
        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            max_length=self.max_length,
            truncation=True,
            padding=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # 平均プーリング
            embeddings = outputs.last_hidden_state.mean(dim=1)
        
        return embeddings.cpu().tolist()
    
    def embed_single(self, text: str) -> List[float]:
        """単一コードをベクトル化"""
        return self.embed_batch([text])[0]
```

**メモリ管理**:
- `torch.no_grad()`: 勾配計算を無効化
- バッチサイズ制御（デフォルト8）
- 大きなコードは自動トランケーション（8192トークン）

**エラーハンドリング**:
```python
try:
    embeddings = self.embed_batch(codes)
except torch.cuda.OutOfMemoryError:
    logger.warning("CUDA OOM, falling back to CPU")
    self.device = "cpu"
    self.model.to(self.device)
    embeddings = self.embed_batch(codes)
```

**パフォーマンス考慮**:
- バッチ処理でスループット向上
- GPU利用時は大幅高速化
- CPU環境でも動作保証

---

### 4.9 indexer/qdrant_indexer.py - Qdrant登録

**責務**: Qdrantへのベクトルとメタデータ登録

**主要メソッド**:

```python
class QdrantIndexer:
    def __init__(self, config: Config):
        """
        Qdrantクライアント初期化
        
        Args:
            config: 設定オブジェクト
        """
        self.config = config
        self.client = QdrantClient(
            url=config.qdrant.url,
            api_key=config.qdrant.api_key
        )
        self.collection_name = config.qdrant.collection_name
        self.dimension = config.embedding.dimension
        
        logger.info(f"Qdrant client initialized: {config.qdrant.url}")
    
    def create_collection(self):
        """
        コレクション作成（既存があれば削除）
        
        処理:
        1. 既存コレクションの確認
        2. 存在する場合は削除
        3. 新規コレクション作成
        
        設定:
        - vector_size: 768
        - distance: COSINE
        """
        # 既存コレクション削除
        collections = self.client.get_collections().collections
        if any(c.name == self.collection_name for c in collections):
            logger.info(f"Deleting existing collection: {self.collection_name}")
            self.client.delete_collection(self.collection_name)
        
        # 新規作成
        logger.info(f"Creating collection: {self.collection_name}")
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.dimension,
                distance=Distance.COSINE
            )
        )
    
    def upsert_batch(
        self, 
        functions: List[FunctionInfo], 
        embeddings: List[List[float]],
        start_id: int = 0
    ):
        """
        バッチでベクトルとメタデータを登録
        
        Args:
            functions: FunctionInfoのリスト
            embeddings: ベクトルのリスト
            start_id: 開始ID
        """
        points = []
        
        for i, (func, embedding) in enumerate(zip(functions, embeddings)):
            points.append(PointStruct(
                id=start_id + i,
                vector=embedding,
                payload=self._build_payload(func)
            ))
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        logger.info(f"Upserted {len(points)} points")
    
    def _build_payload(self, func: FunctionInfo) -> dict:
        """
        FunctionInfoからQdrantペイロードを構築
        
        Returns:
            Qdrantに登録するメタデータ辞書
        """
        return {
            "function_name": func.name,
            "file_path": func.file_path,
            "start_line": func.start_line,
            "end_line": func.end_line,
            "language": func.language,
            "function_type": func.function_type,
            "code": func.code,  # フルコード（検索結果表示用）
            "arguments": func.arguments,
            "return_type": func.return_type,
            "docstring": func.docstring,
            "modifiers": func.modifiers,
            "scope": func.scope,
            "imports": func.imports,
            "calls": func.calls,
            "complexity": func.complexity,
            "loc": func.loc,
            "comment_lines": func.comment_lines
        }
```

**ペイロード構造**:
```json
{
  "function_name": "calculate_statistics",
  "file_path": "/path/to/file.py",
  "start_line": 10,
  "end_line": 25,
  "language": "python",
  "function_type": "function",
  "code": "def calculate_statistics(data): ...",
  "arguments": ["data"],
  "return_type": "dict",
  "docstring": "データの統計情報を計算",
  "modifiers": [],
  "scope": "global",
  "imports": ["statistics", "math"],
  "calls": ["sum", "len"],
  "complexity": 3,
  "loc": 12,
  "comment_lines": 2
}
```

**エラーハンドリング（リトライ機能）**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def upsert_batch(self, ...):
    # 接続エラー時は3回リトライ
    ...
```

---

## 5. 設定ファイル例

### 5.1 config.yaml.example

```yaml
# 入力設定
input:
  source_dir: "/path/to/source/code"
  ignore_file: ".ragignore"

# Qdrant設定
qdrant:
  url: "http://localhost:6333"
  api_key: "${QDRANT_API_KEY}"  # 環境変数から読み込み
  collection_name: "my-project"  # 省略時はディレクトリ名

# 埋め込みモデル設定
embedding:
  model_name: "jinaai/jina-embeddings-v2-base-code"
  dimension: 768
  max_length: 8192
  batch_size: 8

# 処理設定
processing:
  parallel_workers: 4  # CPUコア数に応じて調整
  languages:
    - python
    - rust
    - go
    - java
    - c
    - cpp

# ログ設定
logging:
  level: "INFO"  # DEBUG, INFO, WARN, ERROR
  file: "code-ingest.log"
```

### 5.2 .ragignore.example

```
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
venv/
.venv/

# Rust
target/
Cargo.lock

# Go
*.exe
*.test
vendor/

# Java
*.class
*.jar
target/
.gradle/

# C/C++
*.o
*.a
*.so
*.exe
build/

# テストコード
*_test.py
*_test.go
*Test.java
test_*.py

# 自動生成コード
generated/
*.generated.*
*_pb2.py

# IDEファイル
.vscode/
.idea/
*.swp
```

---

## 6. 実装上の重要な考慮事項

### 6.1 PyTorchバージョン互換性

**問題**: PyTorch 2.1.0が利用不可

**対応**:
- `torch>=2.2.0` を使用
- Jina Embeddings v2 Codeは PyTorch 2.2+ で動作確認済み
- CUDA対応が必要な場合は明示的にインストール

### 6.2 Tree-sitterの初期化

**重要**: 各言語のTree-sitter文法は初回使用時にコンパイルが必要

```python
# 初回実行時に言語文法をビルド
Language.build_library(
    'build/my-languages.so',
    ['tree-sitter-python', 'tree-sitter-rust', ...]
)
```

**対応**:
- パッケージからビルド済みバイナリを使用
- `tree-sitter-python` 等のパッケージがビルド済みを提供

### 6.3 メモリ使用量の管理

**課題**: 大規模コードベース（100万行）での メモリ不足

**対策**:
1. **バッチサイズの動的調整**
   ```python
   if torch.cuda.is_available():
       batch_size = 32
   else:
       batch_size = 8
   ```

2. **ストリーミング処理**
   - ファイル単位で処理→登録を繰り返し
   - 全ファイルをメモリに保持しない

3. **ガベージコレクション**
   ```python
   import gc
   
   # バッチ処理後にメモリ解放
   del embeddings
   gc.collect()
   if torch.cuda.is_available():
       torch.cuda.empty_cache()
   ```

### 6.4 並列処理の注意点

**Tree-sitterはスレッドセーフではない**

**対応**:
- ファイルスキャンのみ並列化
- AST解析は順次処理
- または各プロセスで独立したパーサーインスタンス作成

```python
from concurrent.futures import ProcessPoolExecutor

# NG: スレッド並列（Tree-sitterが非対応）
with ThreadPoolExecutor() as executor:
    results = executor.map(parser.parse_file, files)

# OK: プロセス並列（各プロセスで独立したパーサー）
with ProcessPoolExecutor() as executor:
    results = executor.map(parse_file_wrapper, files)
```

### 6.5 エラーハンドリング戦略

**基本方針**: 部分的な失敗を許容、全体は継続

```python
# ファイル単位のエラー処理
for file_path in files:
    try:
        functions = parser.parse_file(file_path)
        all_functions.extend(functions)
    except Exception as e:
        logger.warning(f"Failed to parse {file_path}: {e}")
        continue  # 次のファイルへ

# 致命的エラーのみ終了
try:
    indexer.create_collection()
except ConnectionError as e:
    logger.error(f"Cannot connect to Qdrant: {e}")
    sys.exit(1)
```

### 6.6 ログ出力のベストプラクティス

**進捗表示**:
```python
total = len(files)
for i, file_path in enumerate(files, 1):
    logger.info(f"[{i}/{total}] Processing {file_path}")
```

**パフォーマンス測定**:
```python
import time

start_time = time.time()
# 処理
elapsed = time.time() - start_time
logger.info(f"Phase completed in {elapsed:.2f} seconds")
```

---

## 7. テスト戦略

### 7.1 テストの種類

| テスト種別 | 対象 | ツール | カバレッジ目標 |
|-----------|------|--------|--------------|
| ユニットテスト | 各モジュール | pytest | >90% |
| 統合テスト | モジュール間連携 | pytest | >80% |
| E2Eテスト | 全体フロー | pytest + Docker | 主要シナリオ |

### 7.2 モックの使用

**モック対象**:
- Qdrant接続: `pytest-mock`
- 埋め込みモデル: `pytest-mock`（重いため）
- ファイルシステム: `pytest-tmp-path`

**例**:
```python
def test_embedder_initialization(mocker):
    # モデルロードをモック
    mock_model = mocker.patch('transformers.AutoModel.from_pretrained')
    mock_tokenizer = mocker.patch('transformers.AutoTokenizer.from_pretrained')
    
    embedder = CodeEmbedder(config)
    
    assert mock_model.called
    assert mock_tokenizer.called
```

### 7.3 テストフィクスチャ

**配置**: `tests/fixtures/`

**内容**:
- `configs/`: テスト用設定ファイル
- `sample_code/`: 各言語のサンプルコード
  - `simple.py`: シンプルな関数
  - `with_class.py`: クラス付き
  - `syntax_error.py`: 構文エラー
  - `sample.rs`, `sample.go`, etc.

---

## 8. 実装の優先順位

### Phase 1: 基盤（1-2日）
1. プロジェクト構造作成
2. logger実装
3. config_loader実装

### Phase 2: ファイル処理（1-2日）
4. file_scanner実装

### Phase 3: パーサー（3-5日）← 最重要
5. base_parser + FunctionInfo
6. python_parser実装
7. 他言語パーサー実装
8. parser_factory実装

### Phase 4: 埋め込み・登録（2-3日）
9. code_embedder実装
10. qdrant_indexer実装

### Phase 5: 統合（1-2日）
11. main.py実装
12. E2Eテスト

### Phase 6: Docker化（1日）
13. Dockerfile, docker-compose
14. ドキュメント

**合計**: 9-15日（1人での実装）

