# 譬ｪ蠑丞・譫舌す繧ｹ繝・Β 螳溯｣・ｨ育判譖ｸ

**繝励Ο繧ｸ繧ｧ繧ｯ繝・*: stock-analysis  
**繝舌・繧ｸ繝ｧ繝ｳ**: 1.0.0  
**菴懈・譌･**: 2025-11-25  
**譛邨よ峩譁ｰ**: 2025-11-25  
**繧ｹ繝・・繧ｿ繧ｹ**: 險育判遒ｺ螳・ 
**蟇ｾ雎｡莨∵･ｭ**: 譚ｱ莠ｬ髮ｻ蜉帙・繝ｼ繝ｫ繝・ぅ繝ｳ繧ｰ繧ｹ・・501・峨∽ｸｭ驛ｨ髮ｻ蜉幢ｼ・502・峨゛ERA・磯撼荳雁ｴ・・
---

## 繝悶Λ繝ｳ繝√ヵ繝ｭ繝ｼ謌ｦ逡･

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#4caf50','primaryTextColor':'#fff','primaryBorderColor':'#2e7d32','lineColor':'#ff00ff','secondaryColor':'#00ff41','tertiaryColor':'#fff'}}}%%
gitGraph
    commit id: "Initial commit"
    branch specs/001-stock-analysis-system
    checkout specs/001-stock-analysis-system
    commit id: "spec.md v1.0.0"
    commit id: "requirements.md"
    
    branch feature/impl-001-stock-analysis-system
    checkout feature/impl-001-stock-analysis-system
    commit id: "plan.md v1.0.0"
    commit id: "Phase 1: 蝓ｺ逶､讒狗ｯ牙ｮ御ｺ・
    commit id: "Phase 2: T007-T012"
    commit id: "Phase 2: T013-T016"
    
    checkout main
    merge feature/impl-001-stock-analysis-system tag: "v1.0.0-mvp"
    
    checkout feature/impl-001-stock-analysis-system
    commit id: "Phase 3: T017-T027 (US1)"
    
    checkout main
    merge feature/impl-001-stock-analysis-system tag: "v1.1.0-us1"
    
    checkout feature/impl-001-stock-analysis-system
    commit id: "Phase 4: T028-T045 (US2)"
    
    checkout main
    merge feature/impl-001-stock-analysis-system tag: "v1.2.0-us2"
    
    checkout feature/impl-001-stock-analysis-system
    commit id: "Phase 5: T046-T058 (US3)"
    commit id: "Phase 6: T059-T072 (US4)"
    
    checkout main
    merge feature/impl-001-stock-analysis-system tag: "v2.0.0-release"
```

**繝悶Λ繝ｳ繝・°逕ｨ繝ｫ繝ｼ繝ｫ**:

| 繝悶Λ繝ｳ繝∝錐 | 逕ｨ騾・| 繝槭・繧ｸ蜈・| 繧ｿ繧ｰ |
|------------|------|----------|------|
| `main` | 譛ｬ逡ｪ迺ｰ蠅・ｼ・itHub Pages蜈ｬ髢具ｼ・| - | `v1.0.0`, `v1.1.0`, ... |
| `specs/001-stock-analysis-system` | 莉墓ｧ倡ｭ門ｮ壹ヶ繝ｩ繝ｳ繝・| `main` | - |
| `feature/impl-001-stock-analysis-system` | 螳溯｣・ヶ繝ｩ繝ｳ繝・ｼ・hase 1-5・・| `main` | User Story螳御ｺ・凾 |

**繧ｿ繧ｰ蜻ｽ蜷崎ｦ丞援**:
- `v1.0.0-mvp`: Phase 1-2螳御ｺ・ｼ亥渕逶､讒狗ｯ・+ 繝・・繧ｿ繝代う繝励Λ繧､繝ｳ・・- `v1.1.0-us1`: User Story 1螳御ｺ・ｼ域律谺｡閾ｪ蜍輔ョ繝ｼ繧ｿ譖ｴ譁ｰ・・- `v1.2.0-us2`: User Story 2螳御ｺ・ｼ医ム繝・す繝･繝懊・繝芽｡ｨ遉ｺ・・- `v2.0.0-release`: 蜈ｨUser Story螳御ｺ・ｼ磯°逕ｨ髢句ｧ具ｼ・
---

## 搭 逶ｮ谺｡

1. [螳溯｣・ヵ繧ｧ繝ｼ繧ｺ](#螳溯｣・ヵ繧ｧ繝ｼ繧ｺ)
2. [謚陦薙せ繧ｿ繝・け](#謚陦薙せ繧ｿ繝・け)
3. [繝励Ο繧ｸ繧ｧ繧ｯ繝域ｧ矩](#繝励Ο繧ｸ繧ｧ繧ｯ繝域ｧ矩)
4. [髢狗匱繝ｯ繝ｼ繧ｯ繝輔Ο繝ｼ](#髢狗匱繝ｯ繝ｼ繧ｯ繝輔Ο繝ｼ)
5. [Constitution v1.0.0繝√ぉ繝・け](#constitution-v100繝√ぉ繝・け)
6. [繝・・繝ｭ繧､繝｡繝ｳ繝域姶逡･](#繝・・繝ｭ繧､繝｡繝ｳ繝域姶逡･)
7. [蜩∬ｳｪ菫晁ｨｼ](#蜩∬ｳｪ菫晁ｨｼ)

---

## 螳溯｣・ヵ繧ｧ繝ｼ繧ｺ

### Phase 1: 蝓ｺ逶､讒狗ｯ・笨・螳御ｺ・
```mermaid
flowchart LR
    A[Python迺ｰ蠅ゾ --> B[Git LFS險ｭ螳咯
    B --> C[SQL繧ｹ繧ｭ繝ｼ繝樔ｽ懈・]
    C --> D[DB蛻晄悄蛹望
    D --> E[繝・ぅ繝ｬ繧ｯ繝医Μ讒矩]
    E --> F[requirements.txt]
    
    style A fill:#4caf50,stroke:#2e7d32,color:#fff
    style B fill:#4caf50,stroke:#2e7d32,color:#fff
    style C fill:#4caf50,stroke:#2e7d32,color:#fff
    style D fill:#4caf50,stroke:#2e7d32,color:#fff
    style E fill:#4caf50,stroke:#2e7d32,color:#fff
    style F fill:#4caf50,stroke:#2e7d32,color:#fff
```

**螳御ｺ・・譫懃黄**:
- `requirements.txt`: Python 3.11萓晏ｭ倬未菫・5繝代ャ繧ｱ繝ｼ繧ｸ
- `.gitattributes`: Git LFS險ｭ螳夲ｼ・.db, *.db.gz・・- `schema.sql`: 8繝・・繝悶Ν + 17繧､繝ｳ繝・ャ繧ｯ繧ｹ
- `scripts/init_db.py`: DB蛻晄悄蛹悶せ繧ｯ繝ｪ繝励ヨ
- `data/db/stock-analysis.db`: 蛻晄悄蛹匁ｸ医∩SQLite・・epco/chubu/jera 3遉ｾ逋ｻ骭ｲ貂医∩・・
---

### Phase 2: 繝・・繧ｿ繝代う繝励Λ繧､繝ｳ 鳩 螳溯｣・ｸｭ

```mermaid
flowchart TB
    subgraph fetch["繝・・繧ｿ蜿門ｾ怜ｱ､"]
        A1[fetch_xbrl.py<br/>EDINET API] 
        A2[fetch_prices.py<br/>Yahoo Finance]
        A3[fetch_market.py<br/>JEPX/LNG萓｡譬ｼ]
    end
    
    subgraph parse["繝・・繧ｿ蜃ｦ逅・ｱ､"]
        B1[parse_xbrl.py<br/>XBRL 竊・JSON]
        B2[normalize_prices.py<br/>譬ｪ萓｡豁｣隕丞喧]
        B3[validate_data.py<br/>繝舌Μ繝・・繧ｷ繝ｧ繝ｳ]
    end
    
    subgraph import["繝・・繧ｿ譬ｼ邏榊ｱ､"]
        C1[import_to_db.py<br/>SQLite UPSERT]
        C2[calculate_ratios.py<br/>雋｡蜍呎欠讓呵ｨ育ｮ余
        C3[calculate_power_metrics.py<br/>髮ｻ蜉帶･ｭ逡梧欠讓呵ｨ育ｮ余
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> B2
    B1 --> B3
    B2 --> B3
    B3 --> C1
    C1 --> C2
    C1 --> C3
    
    style fetch fill:#e3f2fd
    style parse fill:#c8e6c9
    style import fill:#fff9c4
```

**螳溯｣・ち繧ｹ繧ｯ**:

| 繧ｿ繧ｹ繧ｯID | 繧ｹ繧ｯ繝ｪ繝励ヨ蜷・| 隱ｬ譏・| 繧ｹ繝・・繧ｿ繧ｹ | 蜆ｪ蜈亥ｺｦ |
|----------|--------------|------|------------|--------|
| T007 | `scripts/fetch_xbrl.py` | EDINET API縺九ｉXBRL蜿門ｾ・| 譛ｪ逹謇・| P1 |
| T008 | `tests/test_fetch_xbrl.py` | XBRL蜿門ｾ励ユ繧ｹ繝・| 譛ｪ逹謇・| P1 |
| T009 | `scripts/fetch_prices.py` | Yahoo Finance縺九ｉTEPCO/荳ｭ驛ｨ髮ｻ譬ｪ萓｡蜿門ｾ・| 譛ｪ逹謇・| P1 |
| T010 | `tests/test_fetch_prices.py` | 譬ｪ萓｡蜿門ｾ励ユ繧ｹ繝・| 譛ｪ逹謇・| P1 |
| T011 | `scripts/parse_xbrl.py` | XBRL繝代・繧ｹ・・xml菴ｿ逕ｨ縲・1遘・繝輔ぃ繧､繝ｫ・・| 譛ｪ逹謇・| P1 |
| T012 | `tests/test_parse_xbrl.py` | XBRL繝代・繧ｹ繝・せ繝・| 譛ｪ逹謇・| P1 |
| T013 | `scripts/import_to_db.py` | SQLite縺ｸUPSERT・医ヨ繝ｩ繝ｳ繧ｶ繧ｯ繧ｷ繝ｧ繝ｳ蜃ｦ逅・ｼ・| 譛ｪ逹謇・| P1 |
| T014 | `tests/test_import_to_db.py` | DB import繝・せ繝・| 譛ｪ逹謇・| P1 |
| T015 | `scripts/calculate_ratios.py` | ROE/ROA/D/E遲峨・雋｡蜍呎欠讓呵ｨ育ｮ・| 譛ｪ逹謇・| P2 |
| T016 | `scripts/calculate_power_metrics.py` | 譛溘★繧悟ｽｱ髻ｿ鬘・JERA雋｢迪ｮ蠎ｦ險育ｮ・| 譛ｪ逹謇・| P2 |

**謚陦謎ｻ墓ｧ・*:

```python
# scripts/fetch_xbrl.py 螳溯｣・ｾ・import requests
import time
from datetime import datetime

EDINET_API_BASE = "https://api.edinet-fsa.go.jp/api/v2"
EDINET_CODES = {
    "tepco": "E04498",
    "chubu": "E04285",
    "jera": "E36542"
}

def fetch_xbrl_list(target_date: str) -> list:
    """謖・ｮ壽律縺ｮXBRL荳隕ｧ繧貞叙蠕・""
    url = f"{EDINET_API_BASE}/documents.json"
    params = {"date": target_date, "type": "2"}
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    return [
        doc for doc in data.get("results", [])
        if doc["edinetCode"] in EDINET_CODES.values()
    ]

def download_xbrl(doc_id: str, output_dir: str):
    """XBRL繝輔ぃ繧､繝ｫ繧偵ム繧ｦ繝ｳ繝ｭ繝ｼ繝・""
    url = f"{EDINET_API_BASE}/documents/{doc_id}"
    params = {"type": "1"}  # ZIP蠖｢蠑・    
    # 繝ｬ繝ｼ繝亥宛髯宣・螳茨ｼ・遘・1繝ｪ繧ｯ繧ｨ繧ｹ繝茨ｼ・    time.sleep(1)
    
    response = requests.get(url, params=params, stream=True)
    response.raise_for_status()
    
    output_path = f"{output_dir}/{doc_id}.zip"
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return output_path
```

---

### Phase 3: 髮ｻ蜉帶･ｭ逡悟・譫舌お繝ｳ繧ｸ繝ｳ 泯 譛ｪ逹謇・
```mermaid
flowchart TB
    subgraph analyzers["蛻・梵繝｢繧ｸ繝･繝ｼ繝ｫ"]
        A1[jera_period_gap.py<br/>譛溘★繧悟ｽｱ髻ｿ鬘江
        A2[jera_contribution.py<br/>隕ｪ莨夂､ｾ雋｢迪ｮ蠎ｦ]
        A3[fuel_sensitivity.py<br/>辯・侭雋ｻ諢溷ｿ懷ｺｦ]
    end
    
    subgraph metrics["謖・ｨ呵ｨ育ｮ・]
        B1[雋ｩ螢ｲ髮ｻ蜉幃㍼謗ｨ遘ｻ]
        B2[逋ｺ髮ｻ險ｭ蛯吝ｮｹ驥従
        B3[辯・侭雋ｻ隱ｿ謨ｴ鬘江
    end
    
    subgraph output["蜃ｺ蜉・]
        C1[analysis_results.json]
        C2[SQLite譖ｴ譁ｰ<br/>power_industry_metrics]
    end
    
    A1 --> C1
    A2 --> C1
    A3 --> C1
    B1 --> C2
    B2 --> C2
    B3 --> C2
    C1 --> C2
    
    style analyzers fill:#e1bee7
    style metrics fill:#c8e6c9
    style output fill:#fff9c4
```

**螳溯｣・ち繧ｹ繧ｯ**:

| 繧ｿ繧ｹ繧ｯID | 繧ｹ繧ｯ繝ｪ繝励ヨ蜷・| 隱ｬ譏・| 繧ｹ繝・・繧ｿ繧ｹ | 蜆ｪ蜈亥ｺｦ |
|----------|--------------|------|------------|--------|
| T017 | `scripts/analyzers/jera_period_gap.py` | JERA譛溘★繧悟ｽｱ髻ｿ鬘崎ｨ育ｮ・| 譛ｪ逹謇・| P1 |
| T018 | `tests/test_jera_period_gap.py` | 譛溘★繧悟ｽｱ髻ｿ鬘阪ユ繧ｹ繝・| 譛ｪ逹謇・| P1 |
| T019 | `scripts/analyzers/jera_contribution.py` | TEPCO/荳ｭ驛ｨ髮ｻ縺ｸ縺ｮJERA雋｢迪ｮ蠎ｦ險育ｮ・| 譛ｪ逹謇・| P1 |
| T020 | `tests/test_jera_contribution.py` | JERA雋｢迪ｮ蠎ｦ繝・せ繝・| 譛ｪ逹謇・| P1 |
| T021 | `scripts/analyzers/fuel_sensitivity.py` | LNG萓｡譬ｼ諢溷ｿ懷ｺｦ蛻・梵 | 譛ｪ逹謇・| P2 |
| T022 | `tests/test_fuel_sensitivity.py` | 辯・侭雋ｻ諢溷ｿ懷ｺｦ繝・せ繝・| 譛ｪ逹謇・| P2 |

**謚陦謎ｻ墓ｧ・*:

```python
# scripts/analyzers/jera_period_gap.py 螳溯｣・ｾ・def calculate_period_gap_impact(company_id: str, fiscal_year: int, quarter: int) -> float:
    """
    JERA譛溘★繧悟ｽｱ髻ｿ鬘阪ｒ險育ｮ・    
    Args:
        company_id: 'jera'
        fiscal_year: 豎ｺ邂怜ｹｴ蠎ｦ・井ｾ・ 2024・・        quarter: 蝗帛濠譛滂ｼ・-4縲¨one縺ｧ蟷ｴ谺｡・・    
    Returns:
        譛溘★繧悟ｽｱ髻ｿ鬘搾ｼ育卆荳・・・・    
    Formula:
        譛溘★繧悟ｽｱ髻ｿ鬘・= 螳滄圀縺ｮ辯・侭雋ｻ - 辯・侭雋ｻ隱ｿ謨ｴ鬘崎ｻ｢雖∝・
    """
    conn = sqlite3.connect('data/db/stock-analysis.db')
    cursor = conn.cursor()
    
    # 雋｡蜍呵ｫｸ陦ｨ縺九ｉ辯・侭雋ｻ蜿門ｾ・    cursor.execute("""
        SELECT fuel_cost 
        FROM financial_statements 
        WHERE company_id = ? AND fiscal_year = ? AND quarter = ?
    """, (company_id, fiscal_year, quarter))
    
    fuel_cost_actual = cursor.fetchone()[0]
    
    # 蟶ょｴ謖・ｨ吶°繧臥㏍譁呵ｲｻ隱ｿ謨ｴ鬘榊叙蠕暦ｼ育ｰ｡逡･蛹悶∝ｮ滄圀縺ｯ繧医ｊ隍・尅縺ｪ險育ｮ暦ｼ・    cursor.execute("""
        SELECT AVG(lng_price * usd_jpy_rate)
        FROM market_indicators
        WHERE date BETWEEN ? AND ?
    """, (f"{fiscal_year}-01-01", f"{fiscal_year}-12-31"))
    
    fuel_cost_adjusted = cursor.fetchone()[0] * CONVERSION_FACTOR
    
    conn.close()
    
    period_gap_impact = fuel_cost_actual - fuel_cost_adjusted
    return period_gap_impact

# 菴ｿ逕ｨ萓・gap = calculate_period_gap_impact('jera', 2024, None)
print(f"JERA 2024蟷ｴ蠎ｦ譛溘★繧悟ｽｱ髻ｿ鬘・ {gap:,.0f}逋ｾ荳・・")
```

---

### Phase 4: 繝輔Ο繝ｳ繝医お繝ｳ繝・鳩 50%螳御ｺ・
```mermaid
flowchart TB
    subgraph pages["HTML繝壹・繧ｸ"]
        A1[index.html<br/>繝繝・す繝･繝懊・繝云
        A2[tepco.html<br/>譚ｱ莠ｬ髮ｻ蜉幄ｩｳ邏ｰ]
        A3[chubu.html<br/>荳ｭ驛ｨ髮ｻ蜉幄ｩｳ邏ｰ]
        A4[jera.html<br/>JERA隧ｳ邏ｰ]
    end
    
    subgraph js["JavaScript"]
        B1[db-loader.js<br/>sql.js邨ｱ蜷・
        B2[chart-utils.js<br/>Chart.js utilities]
        B3[data-fetcher.js<br/>DB query wrapper]
    end
    
    subgraph css["繧ｹ繧ｿ繧､繝ｫ"]
        C1[styles.css<br/>Tailwind CSS]
        C2[chart-themes.css<br/>繧ｰ繝ｩ繝輔ユ繝ｼ繝枉
    end
    
    A1 --> B1
    A1 --> B2
    A2 --> B1
    A3 --> B1
    A4 --> B1
    B1 --> B3
    A1 --> C1
    B2 --> C2
    
    style pages fill:#e1bee7
    style js fill:#c8e6c9
    style css fill:#fff9c4
```

**螳溯｣・ち繧ｹ繧ｯ**:

| 繧ｿ繧ｹ繧ｯID | 繝輔ぃ繧､繝ｫ蜷・| 隱ｬ譏・| 繧ｹ繝・・繧ｿ繧ｹ | 蜆ｪ蜈亥ｺｦ |
|----------|------------|------|------------|--------|
| T023 | `src/index.html` | 繝｡繧､繝ｳ繝繝・す繝･繝懊・繝・| 笨・ｮ御ｺ・| P1 |
| T024 | `src/styles.css` | 繝ｬ繧ｹ繝昴Φ繧ｷ繝砲SS | 笨・ｮ御ｺ・| P1 |
| T025 | `src/db-loader.js` | sql.js縺ｧSQLite隱ｭ縺ｿ霎ｼ縺ｿ | 譛ｪ逹謇・| P1 |
| T026 | `src/chart-utils.js` | Chart.js繝ｩ繝・ヱ繝ｼ | 譛ｪ逹謇・| P1 |
| T027 | `src/pages/tepco.html` | 譚ｱ莠ｬ髮ｻ蜉幄ｩｳ邏ｰ繝壹・繧ｸ | 譛ｪ逹謇・| P2 |
| T028 | `src/pages/chubu.html` | 荳ｭ驛ｨ髮ｻ蜉幄ｩｳ邏ｰ繝壹・繧ｸ | 譛ｪ逹謇・| P2 |
| T029 | `src/pages/jera.html` | JERA隧ｳ邏ｰ繝壹・繧ｸ | 譛ｪ逹謇・| P1 |
| T030 | `tests/e2e/test_dashboard.py` | E2E繝・せ繝茨ｼ・laywright・・| 譛ｪ逹謇・| P2 |

---

### Phase 5: 閾ｪ蜍募喧繝ｻ騾夂衍 泯 33%螳御ｺ・
```mermaid
flowchart TB
    subgraph actions["GitHub Actions"]
        A1[daily-update.yml<br/>譌･谺｡繝舌ャ繝‐
        A2[deploy.yml<br/>GitHub Pages]
    end
    
    subgraph notify["騾夂衍繧ｷ繧ｹ繝・Β"]
        B1[create_issue.py<br/>Issue菴懈・]
        B2[alert_rules.yaml<br/>繧｢繝ｩ繝ｼ繝医Ν繝ｼ繝ｫ]
    end
    
    subgraph monitoring["逶｣隕・]
        C1[health_check.py<br/>繝倥Ν繧ｹ繝√ぉ繝・け]
        C2[error_handler.py<br/>繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ]
    end
    
    A1 --> B1
    A1 --> C1
    B2 --> B1
    C1 --> C2
    A2 --> C1
    
    style actions fill:#e1bee7
    style notify fill:#fff9c4
    style monitoring fill:#ffccbc
```

**螳溯｣・ち繧ｹ繧ｯ**:

| 繧ｿ繧ｹ繧ｯID | 繝輔ぃ繧､繝ｫ蜷・| 隱ｬ譏・| 繧ｹ繝・・繧ｿ繧ｹ | 蜆ｪ蜈亥ｺｦ |
|----------|------------|------|------------|--------|
| T031 | `.github/workflows/daily-update.yml` | 譌･谺｡繝舌ャ繝・ｼ・ron: "0 9 * * *"・・| 譛ｪ逹謇・| P1 |
| T032 | `.github/workflows/deploy.yml` | GitHub Pages閾ｪ蜍輔ョ繝励Ο繧､ | 笨・ｮ御ｺ・| P1 |
| T033 | `scripts/notify.py` | GitHub Issue菴懈・繧ｹ繧ｯ繝ｪ繝励ヨ | 譛ｪ逹謇・| P2 |
| T034 | `scripts/alert_rules.yaml` | 逡ｰ蟶ｸ讀懃衍繝ｫ繝ｼ繝ｫ螳夂ｾｩ | 譛ｪ逹謇・| P2 |
| T035 | `scripts/error_handler.py` | 繝ｪ繝医Λ繧､繝ｻ繧ｨ繝ｩ繝ｼ繝ｭ繧ｰ | 譛ｪ逹謇・| P2 |
| T036 | `tests/test_integration.py` | 邨ｱ蜷医ユ繧ｹ繝・| 譛ｪ逹謇・| P2 |

---

## 謚陦薙せ繧ｿ繝・け

### 繝舌ャ繧ｯ繧ｨ繝ｳ繝会ｼ・ython 3.11・・
```yaml
core_libraries:
  pandas: "2.1.4"  # 繝・・繧ｿ蜃ｦ逅・  lxml: "4.9.3"    # XBRL隗｣譫・  sqlite3: "built-in"  # 繝・・繧ｿ繝吶・繧ｹ
  
data_fetching:
  requests: "2.31.0"  # HTTP騾壻ｿ｡
  beautifulsoup4: "4.12.2"  # HTML隗｣譫・  yfinance: "0.2.32"  # 譬ｪ萓｡蜿門ｾ・  
testing:
  pytest: "7.4.3"
  pytest-cov: "4.1.0"
  playwright: "1.40.0"  # E2E繝・せ繝・```

### 繝輔Ο繝ｳ繝医お繝ｳ繝・
```yaml
libraries:
  sql_js: "1.8.0"  # 繝悶Λ繧ｦ繧ｶ蜀・QLite
  chart_js: "4.4.0"  # 繧ｰ繝ｩ繝墓緒逕ｻ
  tailwindcss: "3.3.0"  # CSS framework
  
design:
  responsive: true
  mobile_first: true
  accessibility: WCAG 2.1 AA貅匁侠
```

### 繧､繝ｳ繝輔Λ

```yaml
hosting:
  pages: "GitHub Pages"
  actions: "GitHub Actions"
  
storage:
  database: "GitHub LFS"
  archives: "GitHub Releases"
  artifacts: "GitHub Actions Artifacts"
  
ci_cd:
  workflow: "GitHub Actions"
  schedule: "cron: 0 9 * * *"  # 豈取律18:00 JST
```

---

## 繝励Ο繧ｸ繧ｧ繧ｯ繝域ｧ矩

```
stock-analysis/
笏懌楳笏 .github/
笏・  笏披楳笏 workflows/
笏・      笏懌楳笏 daily-update.yml      # 譌･谺｡繝舌ャ繝・笏・      笏披楳笏 deploy.yml            # GitHub Pages繝・・繝ｭ繧､
笏懌楳笏 data/
笏・  笏懌楳笏 db/
笏・  笏・  笏披楳笏 stock-analysis.db     # SQLite・・it LFS邂｡逅・ｼ・笏・  笏懌楳笏 raw/                      # 逕溘ョ繝ｼ繧ｿ・・itignore・・笏・  笏・  笏懌楳笏 xbrl/
笏・  笏・  笏懌楳笏 prices/
笏・  笏・  笏披楳笏 market/
笏・  笏披楳笏 cache/                    # 荳譎ゅヵ繧｡繧､繝ｫ
笏懌楳笏 scripts/
笏・  笏懌楳笏 fetch_xbrl.py
笏・  笏懌楳笏 fetch_prices.py
笏・  笏懌楳笏 parse_xbrl.py
笏・  笏懌楳笏 import_to_db.py
笏・  笏懌楳笏 calculate_ratios.py
笏・  笏懌楳笏 notify.py
笏・  笏披楳笏 analyzers/
笏・      笏懌楳笏 jera_period_gap.py
笏・      笏懌楳笏 jera_contribution.py
笏・      笏披楳笏 fuel_sensitivity.py
笏懌楳笏 src/                          # 繝輔Ο繝ｳ繝医お繝ｳ繝峨た繝ｼ繧ｹ
笏・  笏懌楳笏 index.html
笏・  笏懌楳笏 styles.css
笏・  笏懌楳笏 db-loader.js
笏・  笏懌楳笏 chart-utils.js
笏・  笏披楳笏 pages/
笏・      笏懌楳笏 tepco.html
笏・      笏懌楳笏 chubu.html
笏・      笏披楳笏 jera.html
笏懌楳笏 tests/
笏・  笏懌楳笏 test_fetch_xbrl.py
笏・  笏懌楳笏 test_parse_xbrl.py
笏・  笏懌楳笏 test_import_to_db.py
笏・  笏披楳笏 e2e/
笏・      笏披楳笏 test_dashboard.py
笏懌楳笏 docs/
笏・  笏披楳笏 DEPLOY_GUIDE.md
笏懌楳笏 .specify/
笏・  笏懌楳笏 memory/
笏・  笏・  笏披楳笏 constitution.md       # v1.0.0
笏・  笏披楳笏 templates/
笏懌楳笏 requirements.txt              # Python萓晏ｭ倬未菫・笏懌楳笏 schema.sql                    # DB schema
笏懌楳笏 start.ps1                     # 繝ｯ繝ｳ繧ｳ繝槭Φ繝芽ｵｷ蜍輔せ繧ｯ繝ｪ繝励ヨ
笏披楳笏 README.md
```

---

## 髢狗匱繝ｯ繝ｼ繧ｯ繝輔Ο繝ｼ

### 繝ｭ繝ｼ繧ｫ繝ｫ髢狗匱

```powershell
# 1. 迺ｰ蠅・そ繝・ヨ繧｢繝・・
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. DB蛻晄悄蛹・python scripts/init_db.py

# 3. 繝ｭ繝ｼ繧ｫ繝ｫ繧ｵ繝ｼ繝舌・襍ｷ蜍・python -m http.server 5000

# 4. 繝悶Λ繧ｦ繧ｶ縺ｧ遒ｺ隱・Start-Process "http://localhost:5000/src/index.html"
```

### 繝ｯ繝ｳ繧ｳ繝槭Φ繝芽ｵｷ蜍包ｼ・tart.ps1・・
```powershell
# start.ps1 縺ｮ蜀・ｮｹ
.\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt
Start-Process "http://localhost:5000"
python -m http.server 5000
exit
```

### 繝・せ繝亥ｮ溯｡・
```powershell
# 蜊倅ｽ薙ユ繧ｹ繝・pytest tests/ -v --cov=scripts

# E2E繝・せ繝・playwright install
pytest tests/e2e/ -v
```

---

## Constitution v1.0.0繝√ぉ繝・け

### 蜩∬ｳｪ蜴溷援・・P・画ｺ匁侠

- **QP-001: 谿ｵ髫守噪髢狗匱**
  - 笨・Phase 1-5縺ｫ蛻・牡縲∝推繝輔ぉ繝ｼ繧ｺ迢ｬ遶九＠縺ｦ蜍穂ｽ・  - 笨・Phase 1螳御ｺ・￣hase 2-5縺ｯ萓晏ｭ倬未菫よ・遒ｺ蛹・
- **QP-002: 蜿榊ｾｩ謾ｹ蝟・*
  - 笨・譛菴・蝗槭・繝ｬ繝薙Η繝ｼ繧ｵ繧､繧ｯ繝ｫ・・pec.md, requirements.md, plan.md・・  - 竢ｳ 蜷・ヵ繧ｧ繝ｼ繧ｺ螳溯｣・ｾ後↓繝ｬ繝医Ο繧ｹ繝壹け繝・ぅ繝門ｮ滓命莠亥ｮ・
- **QP-003: 譌･譛ｬ隱槭ラ繧ｭ繝･繝｡繝ｳ繝・*
  - 笨・蜈ｨ莉墓ｧ俶嶌繝ｻ繧ｳ繝｡繝ｳ繝医・螟画焚蜷阪ｒ譌･譛ｬ隱槫喧
  - 笨・闍ｱ隱槭・繝ｬ繝ｼ繧ｹ繝帙Ν繝繝ｼ蜑企勁螳御ｺ・
- **QP-004: 繝医Ξ繝ｼ繧ｵ繝薙Μ繝・ぅ**
  - 笨・spec.md・井ｻ墓ｧ假ｼ俄・ plan.md・郁ｨ育判・俄・ tasks.md・医ち繧ｹ繧ｯ・峨・荳雋ｫ諤ｧ
  - 笨・蜷・ヵ繧｡繧､繝ｫ縺ｫ繝舌・繧ｸ繝ｧ繝ｳ逡ｪ蜿ｷ繝ｻ譖ｴ譁ｰ譌･險倩ｼ・
- **QP-005: 螳溯｡悟庄閭ｽ縺ｪ繧ｳ繝ｼ繝我ｾ・*
  - 笨・spec.md縺ｫ螳溯｡悟庄閭ｽ縺ｪPython/SQL繧ｳ繝ｼ繝我ｾ区軸霈・  - 笨・繧ｳ繝斐・縺ｧ蜍穂ｽ懃｢ｺ隱榊庄閭ｽ

### 繝励Ο繧ｸ繧ｧ繧ｯ繝亥崋譛牙次蜑・ｼ・S・画ｺ匁侠

- **PS-001: 蠅怜・譖ｴ譁ｰ**
  - 笨・SQLite縺九ｉ譛譁ｰ譌･莉伜叙蠕励＠縲∝ｷｮ蛻・・縺ｿ蜿門ｾ励☆繧玖ｨｭ險・  - 竢ｳ 螳溯｣・・ Phase 2縺ｧ蟇ｾ蠢・
- **PS-002: 髮ｻ蜉帶･ｭ逡梧欠讓・*
  - 笨・power_industry_metrics繝・・繝悶Ν險ｭ險亥ｮ御ｺ・  - 竢ｳ Phase 3縺ｧ險育ｮ励Ο繧ｸ繝・け螳溯｣・ｺ亥ｮ・
- **PS-003: JERA蛻・梵**
  - 笨・譛溘★繧悟ｽｱ髻ｿ鬘阪・隕ｪ莨夂､ｾ雋｢迪ｮ蠎ｦ縺ｮ險育ｮ怜ｼ丞ｮ夂ｾｩ螳御ｺ・  - 竢ｳ scripts/analyzers/驟堺ｸ九〒螳溯｣・ｺ亥ｮ・
- **PS-004: 繝・・繧ｿ繝医Ξ繝ｼ繧ｵ繝薙Μ繝・ぅ**
  - 笨・raw_files繝・・繝悶Ν縺ｧ蜈・ョ繝ｼ繧ｿ霑ｽ霍｡
  - 笨・data_source繧ｫ繝ｩ繝縺ｧ蜃ｺ蜈ｸ險倬鹸

- **PS-005: GitHub Issue騾夂衍**
  - 笨・alert_rules螳夂ｾｩ螳御ｺ・  - 竢ｳ scripts/notify.py螳溯｣・ｺ亥ｮ・
### 繧ｻ繧ｭ繝･繝ｪ繝・ぅ蜴溷援・・P・画ｺ匁侠

- **SP-001: API Key菫晁ｭｷ**
  - 笨・GitHub Secrets縺ｧ繧ｭ繝ｼ邂｡逅・  - 竢ｳ .env.example繝輔ぃ繧､繝ｫ菴懈・莠亥ｮ・
- **SP-002: 蜈･蜉帶､懆ｨｼ**
  - 笨・繝舌Μ繝・・繧ｷ繝ｧ繝ｳ繝ｭ繧ｸ繝・け險ｭ險亥ｮ御ｺ・  - 竢ｳ validate_data.py螳溯｣・ｺ亥ｮ・
- **SP-003: 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ**
  - 笨・繝ｪ繝医Λ繧､繝ｻ繝ｭ繧ｰ險ｭ險亥ｮ御ｺ・  - 竢ｳ error_handler.py螳溯｣・ｺ亥ｮ・
- **SP-004: HTTPS騾壻ｿ｡**
  - 笨・GitHub Pages・郁・蜍菱TTPS・・  - 笨・EDINET API・・ttps://・・
---

## 繝・・繝ｭ繧､繝｡繝ｳ繝域姶逡･

### GitHub Actions譌･谺｡繝舌ャ繝・
```yaml
# .github/workflows/daily-update.yml
name: Daily Data Update

on:
  schedule:
    - cron: "0 9 * * *"  # 18:00 JST
  workflow_dispatch:

jobs:
  update-database:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - run: pip install -r requirements.txt
      
      - run: |
          python scripts/fetch_prices.py
          python scripts/fetch_xbrl.py
          python scripts/parse_xbrl.py
          python scripts/import_to_db.py
          python scripts/calculate_ratios.py
          python scripts/analyzers/jera_period_gap.py
      
      - run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add data/
          git commit -m "chore: daily data update $(date +'%Y-%m-%d')" || echo "No changes"
          git push
```

### GitHub Pages閾ｪ蜍輔ョ繝励Ο繧､

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
    paths: ['src/**']

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: 'src'
      - uses: actions/deploy-pages@v4
```

---

## 蜩∬ｳｪ菫晁ｨｼ

### 繝・せ繝域姶逡･

```mermaid
flowchart TB
    subgraph unit["蜊倅ｽ薙ユ繧ｹ繝・]
        A1[test_fetch_xbrl.py]
        A2[test_parse_xbrl.py]
        A3[test_import_to_db.py]
    end
    
    subgraph integration["邨ｱ蜷医ユ繧ｹ繝・]
        B1[test_pipeline.py<br/>繝・・繧ｿ繝輔Ο繝ｼ蜈ｨ菴転
    end
    
    subgraph e2e["E2E繝・せ繝・]
        C1[test_dashboard.py<br/>Playwright]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B1
    B1 --> C1
    
    style unit fill:#c8e6c9
    style integration fill:#fff9c4
    style e2e fill:#e1bee7
```

### 繧ｫ繝舌Ξ繝・ず逶ｮ讓・
- **蜊倅ｽ薙ユ繧ｹ繝・*: 80%莉･荳・- **邨ｱ蜷医ユ繧ｹ繝・*: 荳ｻ隕√ヵ繝ｭ繝ｼ100%
- **E2E繝・せ繝・*: 繝ｦ繝ｼ繧ｶ繝ｼ繧ｹ繝医・繝ｪ繝ｼ1-4繧・00%繧ｫ繝舌・

---

**縺薙・螳溯｣・ｨ育判譖ｸ縺ｯ spec.md縲〉equirements.md 縺ｨ謨ｴ蜷域ｧ繧剃ｿ昴▲縺ｦ縺・∪縺吶・*
**螳溯｣・凾縺ｯ縺薙・險育判縺ｫ蠕薙＞縲・ｲ謐励ｒtasks.md縺ｧ邂｡逅・＠縺ｦ縺上□縺輔＞縲・*

**繝舌・繧ｸ繝ｧ繝ｳ**: 2.0.0 | **菴懈・譌･**: 2025-11-22 | **譛邨よ峩譁ｰ**: 2025-11-22 | **繧ｹ繝・・繧ｿ繧ｹ**: 險育判遒ｺ螳・
