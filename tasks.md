# Code RAG Indexer - 実装タスク一覧（TDD方式）

**開発手法**: テスト駆動開発（TDD - Test-Driven Development）  
**参考**: t_wada氏のTDD原則  
**実装順序**: Red → Green → Refactor

---

## 開発の基本原則

### TDDサイクル

```
1. Red: 失敗するテストを書く
2. Green: テストが通る最小限の実装
3. Refactor: コードを改善（テストは通ったまま）
```

### 実装ルール

- **仮実装を経て本実装へ**: 最初は定数を返す実装でテストを通し、徐々に一般化
- **明白な実装**: シンプルな場合は直接実装
- **三角測量**: 複数のテストケースから実装を導出
- **1つずつ**: 一度に1つのテストだけを追加

---
## Phase 1: ユーティリティ層（基盤）

### Task 1-1: ロガーのテストと実装

**TDDステップ**:

#### Step 1: テスト作成（Red）
**ファイル**: `tests/test_logger.py`

**テストケース**:
1. `test_setup_logger_creates_console_handler`: コンソールハンドラーが作成される
2. `test_setup_logger_creates_file_handler`: ファイルハンドラーが作成される
3. `test_setup_logger_sets_log_level`: ログレベルが正しく設定される
4. `test_get_logger_returns_logger`: モジュール別ロガーが取得できる
5. `test_log_format_is_correct`: ログフォーマットが仕様通り

#### Step 2: 仮実装（Green）
**ファイル**: `src/utils/logger.py`

- 最小限の実装でテストを通す
- まずは固定値を返す実装

#### Step 3: 本実装（Green）
- logging標準ライブラリを使用
- `setup_logger()`, `get_logger()` を実装

#### Step 4: リファクタリング（Refactor）
- 重複コード削除
- 関数分離

**完了条件**:
- [ ] 全テストが通る
- [ ] カバレッジ > 90%

---

## Phase 2: 設定管理層

### Task 2-1: 設定ファイルローダーのテストと実装

**TDDステップ**:

#### Step 1: テスト作成（Red）
**ファイル**: `tests/test_config_loader.py`

**テストケース**:
1. `test_load_valid_config`: 正常な設定ファイルを読み込める
2. `test_load_missing_file_raises_error`: 存在しないファイルで例外
3. `test_expand_env_vars`: 環境変数が展開される
4. `test_default_values`: デフォルト値が適用される
5. `test_collection_name_defaults_to_dirname`: collection_name未指定時にディレクトリ名
6. `test_validate_invalid_source_dir`: 存在しないsource_dirで例外
7. `test_validate_invalid_url`: 不正なURL形式で例外
8. `test_validate_invalid_log_level`: 不正なログレベルで例外

**テストデータ**:
- `tests/fixtures/valid_config.yaml`
- `tests/fixtures/invalid_config.yaml`

#### Step 2: データクラス定義（Green）
**ファイル**: `src/config/config_loader.py`

- 各種Configデータクラスを定義
- 仮実装（固定値返却）

#### Step 3: 本実装（Green）
- YAMLファイル読み込み
- 環境変数展開（正規表現）
- バリデーション実装

#### Step 4: リファクタリング（Refactor）
- バリデーション関数の分離
- エラーメッセージの改善

**完了条件**:
- [ ] 全テストが通る
- [ ] カバレッジ > 90%
- [ ] エッジケースもカバー

---

## Phase 3: ファイルスキャン層

### Task 3-1: ファイルスキャナーのテストと実装

**TDDステップ**:

#### Step 1: テスト作成（Red）
**ファイル**: `tests/test_file_scanner.py`

**テストケース**:
1. `test_scan_finds_python_files`: Pythonファイルを発見
2. `test_scan_finds_multiple_languages`: 複数言語のファイルを発見
3. `test_scan_excludes_ignored_files`: .ragignoreで除外
4. `test_scan_excludes_binary_files`: バイナリファイルを除外
5. `test_is_binary_detects_binary`: バイナリ判定が正しい
6. `test_get_language_returns_correct_language`: 言語判定が正しい
7. `test_load_ignore_patterns_parses_ragignore`: .ragignoreを正しく解析
8. `test_ignore_patterns_match_correctly`: パターンマッチングが正しい

**テストデータ**:
- `tests/fixtures/sample_project/`（テスト用ディレクトリ構造）
  - `src/main.py`
  - `src/lib.rs`
  - `build/binary.exe`（バイナリ）
  - `.ragignore`

#### Step 2: 仮実装（Green）
- 固定リストを返す
- テストが通る最小実装

#### Step 3: 本実装（Green）
- `Path.rglob()` でディレクトリ走査
- `pathspec` ライブラリで.ragignore処理
- バイナリ判定（NULL文字チェック）

#### Step 4: リファクタリング（Refactor）
- 判定ロジックの関数分離
- パフォーマンス改善

**完了条件**:
- [ ] 全テストが通る
- [ ] カバレッジ > 85%

---

## Phase 4: パーサー層（最重要）

### Task 4-1: 基底パーサークラスとFunctionInfoの定義

**TDDステップ**:

#### Step 1: テスト作成（Red）
**ファイル**: `tests/test_base_parser.py`

**テストケース**:
1. `test_function_info_dataclass_creation`: FunctionInfoが作成できる
2. `test_base_parser_is_abstract`: BaseParserが抽象クラス
3. `test_base_parser_parse_file_is_abstract`: parse_fileが抽象メソッド

#### Step 2: 実装（Green）
**ファイル**: `src/parser/base_parser.py`

- FunctionInfoデータクラス定義
- BaseParser抽象基底クラス定義

**完了条件**:
- [ ] テストが通る
- [ ] 型ヒント完備

---

### Task 4-2: Pythonパーサーのテストと実装

**TDDステップ**:

#### Step 1: テスト作成（Red）
**ファイル**: `tests/test_python_parser.py`

**テストケース**:
1. `test_parse_simple_function`: シンプルな関数を解析
2. `test_parse_function_with_arguments`: 引数付き関数を解析
3. `test_parse_function_with_docstring`: docstring付き関数を解析
4. `test_parse_class_method`: クラスメソッドを解析
5. `test_parse_multiple_functions`: 複数関数を解析
6. `test_parse_function_with_comments`: コメント付き関数を解析
7. `test_parse_syntax_error_returns_empty`: 構文エラーで空リスト
8. `test_extract_function_metadata`: メタデータ抽出が正しい

**テストデータ**:
- `tests/fixtures/sample_code/simple.py`
- `tests/fixtures/sample_code/with_class.py`
- `tests/fixtures/sample_code/syntax_error.py`

#### Step 2: 仮実装（Green）
- 固定のFunctionInfoを返す
- Tree-sitter初期化のみ

#### Step 3: 本実装（Green）
- Tree-sitterでパース
- AST走査実装
- FunctionInfo構築

#### Step 4: リファクタリング（Refactor）
- ヘルパーメソッド抽出
- ノード走査ロジックの整理

**完了条件**:
- [ ] 全テストが通る
- [ ] カバレッジ > 80%

---

### Task 4-3: 他言語パーサーの実装（並行作業可能）

**各言語で同様のTDDサイクル**:

#### Rustパーサー
- `tests/test_rust_parser.py`
- `src/parser/rust_parser.py`
- テストフィクスチャ: `tests/fixtures/sample_code/sample.rs`

#### Goパーサー
- `tests/test_go_parser.py`
- `src/parser/go_parser.py`
- テストフィクスチャ: `tests/fixtures/sample_code/sample.go`

#### Javaパーサー
- `tests/test_java_parser.py`
- `src/parser/java_parser.py`
- テストフィクスチャ: `tests/fixtures/sample_code/Sample.java`

#### C/C++パーサー
- `tests/test_c_parser.py`, `tests/test_cpp_parser.py`
- `src/parser/c_parser.py`, `src/parser/cpp_parser.py`
- テストフィクスチャ: `tests/fixtures/sample_code/sample.c`, `sample.cpp`

**各言語の完了条件**:
- [ ] 全テストが通る
- [ ] 基本的な関数解析が動作

---

### Task 4-4: パーサーファクトリのテストと実装

**TDDステップ**:

#### Step 1: テスト作成（Red）
**ファイル**: `tests/test_parser_factory.py`

**テストケース**:
1. `test_get_parser_returns_python_parser`: .pyでPythonパーサー
2. `test_get_parser_returns_rust_parser`: .rsでRustパーサー
3. `test_get_parser_returns_none_for_unknown`: 未知の拡張子でNone
4. `test_detect_language_correct`: 言語判定が正しい
5. `test_parser_singleton`: 同じパーサーインスタンスを返す

#### Step 2: 実装（Green）
**ファイル**: `src/parser/parser_factory.py`

- 拡張子マッピング
- パーサーインスタンス管理
- シングルトンパターン

**完了条件**:
- [ ] 全テストが通る
- [ ] 全言語のパーサーを取得可能

---

## Phase 5: 埋め込み層

### Task 5-1: コード埋め込みのテストと実装

**TDDステップ**:

#### Step 1: テスト作成（Red）
**ファイル**: `tests/test_code_embedder.py`

**テストケース**:
1. `test_embedder_initialization`: モデルが初期化される
2. `test_embed_single_returns_vector`: 単一コードをベクトル化
3. `test_embed_batch_returns_vectors`: バッチでベクトル化
4. `test_vector_dimension_is_768`: ベクトル次元が768
5. `test_embed_long_code_truncates`: 長いコードが切り詰められる
6. `test_embed_with_comments`: コメント付きコードをベクトル化
7. `test_device_selection`: GPU/CPU自動選択

**モック対象**:
- `AutoModel.from_pretrained`: 重いモデルロードをモック
- `AutoTokenizer.from_pretrained`: トークナイザーもモック

#### Step 2: 仮実装（Green）
- ランダムベクトルを返す（768次元）
- モデル初期化のみ

#### Step 3: 本実装（Green）
- Transformersライブラリ使用
- Jina Embeddings v2 Code読み込み
- バッチ処理実装

#### Step 4: リファクタリング（Refactor）
- メモリ管理の改善
- エラーハンドリング追加

**完了条件**:
- [ ] 全テストが通る
- [ ] 実際のモデルでの動作確認（手動）

---

## Phase 6: インデクサー層

### Task 6-1: Qdrantインデクサーのテストと実装

**TDDステップ**:

#### Step 1: テスト作成（Red）
**ファイル**: `tests/test_qdrant_indexer.py`

**テストケース**:
1. `test_indexer_initialization`: クライアントが初期化される
2. `test_create_collection`: コレクションが作成される
3. `test_create_collection_deletes_existing`: 既存コレクションを削除
4. `test_upsert_batch`: バッチでアップサートできる
5. `test_build_payload_correct`: ペイロード構造が正しい
6. `test_connection_error_retry`: 接続エラーでリトライ
7. `test_large_batch_handling`: 大量データの処理

**モック対象**:
- `QdrantClient`: Qdrantサーバーへの接続をモック

#### Step 2: 仮実装（Green）
- 空のメソッド実装
- モック呼び出しのみ

#### Step 3: 本実装（Green）
- Qdrantクライアント実装
- コレクション管理
- バッチアップサート

#### Step 4: リファクタリング（Refactor）
- リトライロジックの整理
- エラーハンドリング強化

**完了条件**:
- [ ] 全テストが通る
- [ ] 実際のQdrantでの動作確認（手動）

---

## Phase 7: メイン処理

### Task 7-1: メイン処理のテストと実装

**TDDステップ**:

#### Step 1: 統合テスト作成（Red）
**ファイル**: `tests/test_main.py`

**テストケース**:
1. `test_parse_arguments`: 引数解析が正しい
2. `test_main_success_flow`: 正常系の全体フロー
3. `test_main_missing_config`: 設定ファイル未存在でエラー
4. `test_main_scan_files`: ファイルスキャンが実行される
5. `test_main_parse_files`: パース処理が実行される
6. `test_main_embed_and_index`: 埋め込みと登録が実行される
7. `test_main_returns_zero_on_success`: 成功時に0を返す
8. `test_main_returns_one_on_error`: エラー時に1を返す

**モック対象**:
- すべての依存モジュール（統合テストのため）

#### Step 2: 仮実装（Green）
- 各フェーズのスタブ呼び出し
- ログ出力のみ

#### Step 3: 本実装（Green）
- 全モジュールの統合
- エラーハンドリング
- 進捗表示

#### Step 4: リファクタリング（Refactor）
- 関数分割
- エラーメッセージの改善

**完了条件**:
- [ ] 全テストが通る
- [ ] E2Eテストで実際のコードが登録される

---

## Phase 8: 統合テスト・E2Eテスト

### Task 8-1: E2Eテストの作成と実行

**テストシナリオ**:

#### Scenario 1: 小規模プロジェクトの登録
1. テスト用の小さなプロジェクトを用意
2. 設定ファイル作成
3. 実行
4. Qdrantに正しくデータが登録されているか確認

#### Scenario 2: エラーケース
1. 構文エラーを含むファイル
2. バイナリファイル混在
3. 除外パターン適用

**ファイル**: `tests/test_e2e.py`

**完了条件**:
- [ ] 実際のQdrantサーバーでテスト成功
- [ ] エラーケースも正しく処理

---

## Phase 9: Docker化・ドキュメント

### Task 9-1: Dockerfile作成

**ファイル**: `Dockerfile`

**内容**:
- Python 3.11ベースイメージ
- 依存パッケージインストール
- アプリケーションコピー

### Task 9-2: docker-compose.yml作成

**ファイル**: `docker-compose.yml`

**サービス**:
- qdrant: Qdrantサーバー
- indexer: Code RAG Indexer

### Task 9-3: README作成

**ファイル**: `README.md`

**内容**:
- プロジェクト概要
- インストール方法
- 使用方法
- 設定例
- トラブルシューティング

### Task 9-4: サンプル設定ファイル

**ファイル**:
- `config.yaml.example`
- `.ragignore.example`

---

## 実装順序サマリー

```
Phase 0: セットアップ (1タスク)
  └─ Task 0-1: プロジェクト構造

Phase 1: ユーティリティ (1タスク)
  └─ Task 1-1: ロガー

Phase 2: 設定管理 (1タスク)
  └─ Task 2-1: 設定ローダー

Phase 3: ファイルスキャン (1タスク)
  └─ Task 3-1: ファイルスキャナー

Phase 4: パーサー (4タスク) ← 最重要・最大ボリューム
  ├─ Task 4-1: 基底クラス
  ├─ Task 4-2: Pythonパーサー
  ├─ Task 4-3: 他言語パーサー (並行可能)
  └─ Task 4-4: パーサーファクトリ

Phase 5: 埋め込み (1タスク)
  └─ Task 5-1: コード埋め込み

Phase 6: インデクサー (1タスク)
  └─ Task 6-1: Qdrantインデクサー

Phase 7: メイン処理 (1タスク)
  └─ Task 7-1: メイン処理

Phase 8: 統合テスト (1タスク)
  └─ Task 8-1: E2Eテスト

Phase 9: Docker・ドキュメント (4タスク)
  ├─ Task 9-1: Dockerfile
  ├─ Task 9-2: docker-compose
  ├─ Task 9-3: README
  └─ Task 9-4: サンプル設定
```

**総タスク数**: 16タスク  
**推定工数**: 1-2週間（1人での実装）

---

## Claude Codeへの実装依頼時の指示

各Phaseを順番に実装依頼する際は、以下の形式で指示してください：

```
【Phase X: XXXX の実装】

以下のTDD方式で実装してください：

1. テストファイル `tests/test_XXX.py` を作成
   - テストケース: [リスト]
   - テストフィクスチャ: [必要なデータ]

2. 実装ファイル `src/XXX/XXX.py` を作成
   - 仮実装 → 本実装 → リファクタリング

3. 完了条件:
   - すべてのテストがpassすること
   - カバレッジが XX% 以上であること

参考情報:
- 要件定義書: [該当箇所]
- 基本設計書: [該当箇所]
```

この順序で実装を進めることで、堅牢で保守性の高いコードが完成します。