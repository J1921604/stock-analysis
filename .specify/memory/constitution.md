# 株式分析システム開発憲法 (Stock Analysis System Constitution)

**バージョン**: 1.0.0
**批准日**: 2025年11月22日
**最終改訂**: 2025年11月22日
**プロジェクト名**: stock-analysis
**目的**: 日本上場銘柄の自動解析システム開発における品質・セキュリティ・ガバナンス基準

---

## 🎯 品質原則 (Quality Principles)

### QP-001: 完全性重視
**原則**: ワークスペース内の全ファイルを末尾まで解析する
**実装**: トークン制限まで中断せず全てのタスクを実行する
**禁止事項**: トークン制限による中断、簡略化、品質低下は一切許容しない

### QP-002: 継続的改善
**原則**: トークン制限まで、生成したドキュメントを繰り返しブラッシュアップする
**実装**: 
- 初回生成後、最低3回のレビュー・改善サイクルを実施
- 各サイクルで具体性、正確性、再現性を向上
- ベストプラクティスとの整合性を確認

**改善サイクル例**:
```yaml
cycle_1_初回生成:
  spec.md: 基本構造作成、テンプレートから生成
  issues: プレースホルダー残存、コード例不足

cycle_2_具体化:
  spec.md: プレースホルダー削除、コード例追加
  issues: エラーハンドリング不足、パフォーマンス閾値曖昧

cycle_3_精度向上:
  spec.md: try-catch追加、閾値定量化（< 2秒）
  issues: Mermaid図の視認性低下

cycle_4_最適化:
  spec.md: Mermaid図に色分け追加、一貫性チェック
  status: トークン制限に達するまで継続

quality_gates:
  - プレースホルダー完全削除
  - 全コード例が実行可能
  - 閾値が全て定量化
  - ドキュメント間の整合性確認
```

### QP-003: 文字化け対策
**原則**: 全ドキュメント・コードファイルをUTF-8エンコーディングで保存
**実装**:
```yaml
encoding_standards:
  markdown: UTF-8 (BOM無し)
  python: UTF-8 (BOM無し)
  yaml: UTF-8 (BOM無し)
  json: UTF-8 (BOM無し)
```

### QP-004: テンプレート純化
**原則**: テンプレートから生成したドキュメントの英語部分を確実に削除する
**実装**:
- プレースホルダー (`[Description]`, `TBD`, `TODO`) の完全置換
- サンプルテキストの日本語化
- 混在言語の統一（日本語優先）

### QP-005: テスト駆動開発徹底
**原則**: 仕様に対する検証を必須とする
**実装**:
```yaml
test_coverage:
  minimum: 100%
  unit_tests: 必須
  integration_tests: 必須
  edge_case_tests: 必須
test_execution:
  on_commit: true
  on_pull_request: true
  before_deploy: true
```

---

## 🔒 セキュリティ原則 (Security Principles)

### SP-001: 優先順位
**原則**: セキュリティ要件を機能要件より優先する
**実装順序**:
1. セキュリティ設計
2. 認証・認可実装
3. 機能実装
4. パフォーマンス最適化

### SP-002: 機密データ保護
**原則**: 機密データの平文保存を禁止（暗号化・ハッシュ化必須）
**実装**:
```yaml
encryption_requirements:
  api_keys: 環境変数またはSecrets Manager
  database_credentials: 暗号化保存
  presigned_urls: 7日間有効期限
  personal_data: 暗号化 + ハッシュ化
```

### SP-003: 入力検証
**原則**: 全ての外部入力に対してバリデーションを実施
**実装**:
- XBRLファイル: スキーマ検証
- 株価データ: 型・範囲検証
- ユーザー入力: サニタイズ + エスケープ

**具体的実装例**:
```python
# XBRLスキーマ検証
from lxml import etree

def validate_xbrl(xbrl_file: str) -> bool:
    """XBRLファイルのスキーマ検証"""
    try:
        schema = etree.XMLSchema(file='schemas/xbrl-schema.xsd')
        doc = etree.parse(xbrl_file)
        is_valid = schema.validate(doc)
        
        if not is_valid:
            logger.warning(f"XBRL validation failed: {schema.error_log}")
        
        return is_valid
    except Exception as e:
        logger.error(f"XBRL validation error: {str(e)}")
        return False

# 株価データ範囲検証
def validate_stock_price(price_data: dict) -> bool:
    """株価データの型・範囲検証"""
    checks = [
        ('date', lambda x: isinstance(x, str) and len(x) == 10),  # YYYY-MM-DD
        ('close', lambda x: isinstance(x, (int, float)) and 0 < x < 1000000),
        ('volume', lambda x: isinstance(x, int) and x >= 0),
    ]
    
    for field, validator in checks:
        if field not in price_data or not validator(price_data[field]):
            logger.error(f"Validation failed for {field}: {price_data.get(field)}")
            return False
    
    return True

# SQLインジェクション対策
def safe_query(company_id: str) -> list:
    """パラメータ化クエリ使用"""
    # ❌ 危険: 文字列連結
    # sql = f"SELECT * FROM companies WHERE company_id = '{company_id}'"
    
    # ✅ 安全: パラメータ化
    sql = "SELECT * FROM companies WHERE company_id = ?"
    return db.execute(sql, (company_id,)).fetchall()
```

### SP-004: エラーハンドリング
**原則**: 全ての例外を適切にキャッチし、機密情報を含まないログを出力
**実装**:
```python
try:
    # 処理
except Exception as e:
    logger.error(f"処理失敗: {type(e).__name__}")  # ✅ 一般的なエラー
    # logger.error(f"失敗: {api_key}")  # ❌ 機密情報露出
```

---

## ⚡ パフォーマンス原則 (Performance Principles)

### PP-001: 定量化
**原則**: パフォーマンス閾値を定量化し、受入基準に組み込む
**実装**:
```yaml
performance_thresholds:
  initial_load: < 2秒
  crud_operations: < 100ms
  data_filtering_1000_items: < 200ms
  memory_usage: < 50MB
  github_actions_build: < 5分
```

### PP-002: 測定と監視
**原則**: 全ての重要処理に対してパフォーマンス測定を実装
**実装**:
```python
from utils.performance import measurePerformanceSync
import time
import logging

logger = logging.getLogger(__name__)

def measurePerformanceSync(func, operation_name: str, threshold_ms: float = 1000):
    """
    パフォーマンス測定ユーティリティ
    
    Args:
        func: 測定対象の関数
        operation_name: 操作名（ログ用）
        threshold_ms: 閾値（ミリ秒）
    
    Returns:
        関数の実行結果
    """
    start = time.perf_counter()
    
    try:
        result = func()
        duration_ms = (time.perf_counter() - start) * 1000
        
        # 閾値超過時に警告
        if duration_ms > threshold_ms:
            logger.warning(
                f"Performance threshold exceeded: {operation_name} "
                f"took {duration_ms:.2f}ms (threshold: {threshold_ms}ms)"
            )
        else:
            logger.info(f"{operation_name} completed in {duration_ms:.2f}ms")
        
        return result
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.error(
            f"{operation_name} failed after {duration_ms:.2f}ms: {str(e)}"
        )
        raise

# 使用例
result = measurePerformanceSync(
    lambda: analyze_xbrl(file),
    "XBRL解析",
    threshold_ms=1000
)
```

**GitHub Actionsでの測定例**:
```yaml
# .github/workflows/daily-update.yml
- name: Run analysis with timing
  run: |
    start_time=$(date +%s)
    python scripts/analyze.py --db data/db/stock-analysis.db --output analysis-results.json
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    echo "Analysis duration: ${duration}s" >> $GITHUB_STEP_SUMMARY
    
    if [ $duration -gt 180 ]; then
      echo "⚠️ Analysis took longer than 3 minutes" >> $GITHUB_STEP_SUMMARY
    fi
```

### PP-003: 最適化優先順位
**原則**: ボトルネック特定後、影響の大きい順に最適化
**実装**:
1. データベースクエリ最適化（インデックス追加）
2. アルゴリズム改善（O(n²) → O(n log n)）
3. キャッシング導入
4. 並列処理化

---

## 🚫 制約事項 (Constraints)

### CS-001: 外部依存管理
**原則**: 外部依存はバージョン固定により再現性を確保する
**実装**:
```json
// package.json
{
  "dependencies": {
    "react": "18.2.0",  // ✅ 固定バージョン
    "typescript": "4.9.3"  // ✅ 固定バージョン
  }
}
```
```txt
# requirements.txt
pandas==2.0.3  # ✅ 固定バージョン
lxml==4.9.3  # ✅ 固定バージョン
```

### CS-002: 仕様と実装の整合性
**原則**: 仕様と実装の乖離をレビューで検知・是正する
**実装**:
- Pull Request時に仕様書との差分確認
- テストケースで仕様準拠を検証
- 月次で仕様書更新レビュー

### CS-003: ストレージ戦略（GitHub活用）
**原則**: AWS S3の代わりにGitHub機能を最大限活用する
**実装**:

```mermaid
flowchart TD
    A[ストレージ戦略] --> B[GitHub Releases]
    A --> C[GitHub LFS]
    A --> D[GitHub Actions Artifacts]
    
    B --> B1[大容量ファイル保存<br/>XBRLアーカイブ tar.gz]
    C --> C1[SQLiteファイル<br/>バージョン管理]
    D --> D1[CI/CD一時ファイル<br/>90日保持]
    
    style A fill:#e1bee7
    style B fill:#c8e6c9
    style C fill:#c8e6c9
    style D fill:#c8e6c9
```

**詳細実装**:
```yaml
storage_strategy:
  github_releases:
    use_case: 年次XBRLアーカイブ保存
    format: tar.gz
    retention: 永久
    max_size: 2GB/ファイル
    naming: "xbrl-archive-{YYYY}.tar.gz"
    
  github_lfs:
    use_case: SQLiteデータベース
    format: sqlite.gz
    versioning: true
    max_size: 2GB/ファイル
    auto_push: GitHub Actions経由
    
  github_actions_artifacts:
    use_case: ビルド成果物、一時ファイル
    retention: 90日
    naming: "build-{date}-{run_id}"
```

---

## 🏛️ ガバナンス原則 (Governance Principles)

### GP-001: 作業順序の厳守
**原則**: 憲法 → 仕様 → 計画 → タスク → 検証 → 実装 → レビュー

```mermaid
flowchart LR
    A[憲法作成] --> B[仕様書作成]
    B --> C[開発計画]
    C --> D[タスク分解]
    D --> E[検証計画]
    E --> F[実装]
    F --> G[コードレビュー]
    G --> H{品質基準満たす?}
    H -->|Yes| I[マージ]
    H -->|No| F
    
    style A fill:#e1bee7
    style B fill:#ce93d8
    style I fill:#c8e6c9
```

### GP-002: ブランチ戦略
**原則**: 仕様と実装はブランチで分離する
**実装**:
```bash
# 仕様ブランチ（mainから派生）
git checkout main
git checkout -b spec/001-stock-analysis-system

# 実装ブランチ（仕様ブランチから派生）
git checkout spec/001-stock-analysis-system
git checkout -b feature/impl-001-stock-analysis-system
```

**命名規則**:
```yaml
branch_naming:
  spec: "spec/<番号>-<短い名前>"
  feature: "feature/impl-<番号>-<短い名前>"
  fix: "fix/<番号>-<短い名前>"
  docs: "docs/<番号>-<短い名前>"

examples:
  - "spec/001-stock-analysis-system"
  - "feature/impl-001-xbrl-parser"
  - "fix/002-memory-leak"
  - "docs/003-deployment-guide"
```

### GP-003: レビュー承認
**原則**: 重大変更にはレビュー承認を必須とする
**重大変更の定義**:
- データベーススキーマ変更
- ストレージ戦略変更
- セキュリティ関連の変更
- パフォーマンス要件の変更

**レビュー基準**:
```yaml
review_checklist:
  code_quality:
    - 型安全性の確保
    - エラーハンドリングの実装
    - テストカバレッジ100%
  security:
    - 機密情報の保護
    - 入力検証の実装
    - 認証・認可の確認
  performance:
    - 閾値の遵守
    - メモリリークの検証
    - 大量データでの動作確認
  documentation:
    - コードコメントの充実
    - README更新
    - 仕様書との整合性
```

**レビュー実施例**:
```yaml
pull_request_example:
  title: "feat: Add Net-Net PBR calculation"
  
  reviewer_checklist:
    - question: "型安全性は確保されているか？"
      check: "全関数に型ヒント、mypy合格"
      status: ✅
    
    - question: "エラーハンドリングは適切か？"
      check: "try-except実装、ログ出力あり"
      status: ✅
    
    - question: "テストカバレッジは100%か？"
      check: "pytest --cov で確認"
      status: ✅
    
    - question: "パフォーマンス閾値を満たすか？"
      check: "計算時間 < 1秒/銘柄"
      status: ✅
    
    - question: "仕様書との整合性は？"
      check: "spec.md の数式と一致"
      status: ✅
  
  review_result: "Approved"
  merge_decision: "Merge to feature/impl-001-stock-analysis-system"
```

---

## 🚀 開発方針 (Development Policy)

### DP-001: ワンコマンド起動
**原則**: localhost起動後、PowerShellを自動で閉じるスクリプトを提供
**実装**:
```powershell
# start.ps1
Write-Host "株式分析システムを起動します..." -ForegroundColor Green

# 環境チェック（Python 3.11+, Git確認）
python --version

# 仮想環境アクティベート
& .\venv\Scripts\Activate.ps1

# 依存関係インストール
pip install -q -r requirements.txt

# ブラウザでlocalhostを開く
Start-Process "http://localhost:5000"

# 開発サーバー起動（Python簡易HTTPサーバー）
Push-Location src
python -m http.server 5000
Pop-Location

# サーバー停止後、PowerShellを閉じる
exit
```

**ワンコマンド起動の利点**:
- 環境構築を自動化（venv作成、pip install）
- 開発者体験の向上（コマンド1つで即座にローカル起動）
- ドキュメント不要（start.ps1を実行するだけ）

### DP-002: 継続的検証
**原則**: 正常に動作するまで繰り返し検証しエラー修正を完了する
**実装**:
```yaml
verification_loop:
  steps:
    1. 機能実装
    2. ユニットテスト実行
    3. 統合テスト実行
    4. 手動動作確認
    5. エラーがあれば1に戻る
    6. 全て成功で次のタスクへ
```

### DP-003: Mermaid図v11準拠
**原則**: フローチャートなどMermaid図v11準拠を挿入する
**ベストプラクティス**:
```yaml
mermaid_v11_guidelines:
  avoid_in_gitgraph:
    - 日本語の使用（バグの原因）
    - tag構文（非推奨）
  
  recommended_for_japanese:
    - flowchart TB/TD/LR
    - graph TB/TD/LR
    - sequenceDiagram
    - stateDiagram-v2
  
  color_palette:
    primary: "#e1bee7"      # 紫系（重要セクション）
    success: "#c8e6c9"      # 緑系（完了・実装）
    warning: "#fff9c4"      # 黄系（注意・分析）
    info: "#e3f2fd"         # 青系（情報・データ）
    secondary: "#ffccbc"    # オレンジ系（処理・変換）
    neutral: "#b2dfdb"      # 緑青系（補助要素）
```

**Mermaid図の品質基準**:
- 全ノードに日本語ラベル（英語避ける）
- subgraphで論理的グルーピング
- 色分けで視認性向上
- 矢印に説明テキスト（必要時のみ）

### DP-004: ドキュメント生成品質
**原則**: 生成したドキュメントは以下の基準を満たす
**品質基準**:
```yaml
document_quality_standards:
  completeness:
    - 全セクションに具体的な内容
    - プレースホルダー完全排除
    - サンプルコードの実行可能性
  
  accuracy:
    - 技術用語の正確性
    - コード例の動作検証済み
    - 外部リンクの有効性確認
  
  reproducibility:
    - 他AIが再現可能なレベルの詳細度
    - 環境構築手順の完全性
    - トラブルシューティング情報の充実
  
  consistency:
    - 用語の統一
    - コーディング規約の一貫性
    - ドキュメント間の整合性
  
  maintainability:
    - バージョン情報の明記
    - 更新日時の記載
    - 変更履歴の管理
```

---

## 📊 測定と監視 (Measurement & Monitoring)

### MM-001: 品質メトリクス
```yaml
quality_metrics:
  code_coverage: 100%
  type_safety: 完全（Python型ヒント、TypeScript strict mode）
  documentation_coverage: 全public API
  test_pass_rate: 100%
```

### MM-002: パフォーマンスメトリクス
```yaml
performance_metrics:
  initial_load_time: < 2秒
  xbrl_parse_time: < 1秒/ファイル
  data_filtering_1000_items: < 200ms
  memory_usage: < 50MB
  github_actions_build: < 5分
```

### MM-003: セキュリティメトリクス
```yaml
security_metrics:
  vulnerability_count: 0
  dependency_audit: 毎週実行
  secrets_scan: 毎コミット
  encryption_coverage: 機密データ100%
```

---

## 🔄 継続的改善 (Continuous Improvement)

### CI-001: 定期レビュー
**頻度**: 月次
**対象**:
- 憲法の妥当性
- 仕様書の正確性
- テストカバレッジ
- パフォーマンス指標

### CI-002: フィードバックループ
```mermaid
flowchart LR
    A[実装] --> B[測定]
    B --> C[分析]
    C --> D[改善案]
    D --> E[憲法・仕様更新]
    E --> A
    
    style A fill:#e3f2fd
    style C fill:#fff9c4
    style E fill:#c8e6c9
```

**フィードバックループ実施例**:
```yaml
iteration_1:
  implementation:
    feature: "NetNetPBR計算実装"
    code: "scripts/analyze.py"
  
  measurement:
    metric: "計算時間"
    result: "5秒/銘柄"
    threshold: "< 1秒/銘柄"
    status: "❌ 閾値超過"
  
  analysis:
    bottleneck: "データベースクエリが遅い"
    evidence: "SQLクエリが全行スキャン"
    tool: "EXPLAIN QUERY PLAN"
  
  improvement:
    proposal: "インデックス追加"
    implementation: "CREATE INDEX idx_financials_company_date"
    expected: "5秒 → 0.5秒"
  
  documentation_update:
    spec_md: "データベーススキーマにインデックス追記"
    constitution_md: "パフォーマンス測定例を追加"

iteration_2:
  implementation:
    feature: "インデックス追加"
    code: "schemas/create_indexes.sql"
  
  measurement:
    metric: "計算時間"
    result: "0.4秒/銘柄"
    threshold: "< 1秒/銘柄"
    status: "✅ 合格"
  
  analysis:
    result: "目標達成"
    next_focus: "チャート描画速度"
  
  improvement:
    proposal: "次のボトルネックに取り組む"
  
  documentation_update:
    spec_md: "パフォーマンス実績を記載"
```

### CI-003: 技術負債管理
```yaml
technical_debt_policy:
  identification:
    - 毎PR時にコードレビューで検出
    - 四半期ごとに負債棚卸し
  
  prioritization:
    critical: セキュリティ・パフォーマンス影響大
    high: 保守性・拡張性阻害
    medium: コード品質低下
    low: 軽微な改善余地
  
  resolution:
    critical: 即時対応（1週間以内）
    high: 1ヶ月以内
    medium: 3ヶ月以内
    low: 機会があれば対応
```

---

## ガバナンス (Governance)

この憲法は全ての開発プラクティスに優先します。
憲法の改訂には以下が必要です:
- 改訂提案のドキュメント化
- プロジェクトリードの承認
- 既存コードへの移行計画

全てのPull Request・コードレビューは本憲法への準拠を検証する必要があります。

---

**バージョン**: 1.0.0 | **批准日**: 2025年11月22日 | **最終改訂**: 2025年11月22日
