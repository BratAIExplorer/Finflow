# Financial Services Skills Guide for FinFlow

**For FinFlow**, the most relevant installed skills are organized by use case:

## 💰 Portfolio & Fund Management

```bash
/portfolio-monitoring     # Track holdings, positions, performance
/portfolio-rebalance      # Asset allocation optimization
/nav-tieout              # Net Asset Value calculations
/returns-analysis        # Performance metrics (CAGR, Sharpe, attribution)
/unit-economics          # Economics per-unit analysis
```

## 📊 Valuation & Modeling

```bash
/dcf-model               # DCF valuation with projections
/lbo-model               # Leveraged buyout analysis
/comps-analysis          # Comparable company multiples
/merger-model            # M&A financial model
/3-statement-model       # Income statement + Balance sheet + Cash flow
/break-trace             # Root-cause reconciliation breaks
```

## 📈 Financial Analysis

```bash
/earnings-analysis       # Quarterly/annual earnings analysis
/earnings-preview        # Pre-earnings expectations
/competitive-analysis    # Competitor landscape
/sector-overview         # Industry benchmarking
/variance-commentary     # Budget vs actual narrative
/financial-plan          # Budgeting & forecasting
```

## 🏢 Operations & Compliance

```bash
/gl-recon                # GL to subledger reconciliation
/accrual-schedule        # Month-end accrual entries
/audit-xls               # Spreadsheet validation & audit
/kyc-doc-parse           # KYC/AML document parsing
/kyc-rules               # Compliance rule checking
/dd-checklist            # Due diligence tracker
```

## 📋 Reporting & Clients

```bash
/client-report           # Performance reports for investors
/client-review           # Quarterly review materials
/pitch-deck              # Investment pitch presentation
/cim-builder             # Confidential Information Memo
/teaser                  # Deal teaser/executive summary
```

## 🛠️ Spreadsheet & Data Tools

```bash
/xlsx-author             # Excel workbook creation
/pptx-author             # PowerPoint presentation creation
/audit-xls               # Formula checking & validation
/clean-data-xls          # Data cleanup (trim, dedupe, normalize)
/datapack-builder        # Build normalized financial data packs
```

## 🔄 Integration with FinFlow

### In FastAPI Endpoints

```python
from fastapi import FastAPI
from claude.integrations import claude_skill

app = FastAPI()

# Valuation endpoint
@app.post("/api/valuations/dcf")
async def get_dcf_valuation(company_id: str):
    valuation = await claude_skill('dcf-model', {
        'company_id': company_id,
        'projection_years': 5,
        'wacc': 0.08
    })
    return valuation

# Portfolio analysis endpoint
@app.get("/api/portfolios/{portfolio_id}/analysis")
async def analyze_portfolio(portfolio_id: str):
    analysis = await claude_skill('portfolio-monitoring', {
        'portfolio_id': portfolio_id,
        'include_rebalancing': True
    })
    return analysis

# GL reconciliation endpoint
@app.post("/api/accounting/reconcile")
async def reconcile_accounts(account_id: str, period: str):
    recon = await claude_skill('gl-recon', {
        'account': account_id,
        'period': period
    })
    return recon
```

### In Client Reports

```python
# Generate client performance report
report = await claude_skill('client-report', {
    'portfolio_id': portfolio.id,
    'include_allocations': True,
    'include_commentary': True,
    'period': 'Q2 2026'
})
```

### For Data Analysis

```python
# Build normalized financial data pack
datapack = await claude_skill('datapack-builder', {
    'source_documents': [cim, offering_memo],
    'normalize_dates': True,
    'validate_calculations': True
})
```

## 🚀 Quick Start

1. **In Claude Code (any session):**
   ```bash
   /portfolio-monitoring        # Try it immediately
   /dcf-model --help           # See parameters
   ```

2. **In Cowork (multi-agent workflows):**
   ```bash
   @earnings-reviewer: Analyze Q2 2026 earnings for portfolio
   @gl-reconciler: Month-end close for fund
   @portfolio-monitoring: Rebalance recommendations
   ```

3. **In FinFlow Feature Development:**
   - Use skills in FastAPI endpoints
   - Chain skills for complex workflows
   - Cache results for performance

## 📚 Full Documentation

For complete details on all installed skills/agents:

```bash
cat ~/.claude/FINSERVICES_INSTALLATION.md
```

## 🔗 Available Agents

Pre-built agents for complex workflows (launch in Cowork):

```bash
~/.claude/agents/finservices/pitch-agent              # M&A pitch decks
~/.claude/agents/finservices/earnings-reviewer        # Earnings analysis
~/.claude/agents/finservices/gl-reconciler            # GL reconciliation
~/.claude/agents/finservices/month-end-closer         # Automated close
~/.claude/agents/finservices/portfolio-monitoring     # Portfolio review
~/.claude/agents/finservices/market-researcher        # Market analysis
~/.claude/agents/finservices/model-builder            # Financial modeling
~/.claude/agents/finservices/kyc-screener             # Compliance screening
~/.claude/agents/finservices/statement-auditor        # Audit & review
~/.claude/agents/finservices/valuation-reviewer       # Deal valuation
```

---

**Status:** ✅ 193 skills + 10 agents installed and ready to use
