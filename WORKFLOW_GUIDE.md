# Daily Workflow Guide

## Overview

The `workflow_daily.py` script automates the complete daily process of:
1. **Consolidating** today's job descriptions from the catalog
2. **Improving** your portfolio repository based on today's JDs
3. **Pushing** changes to GitHub

## Quick Start

### Run Full Workflow
```bash
cd quant_scraper
python workflow_daily.py
```

This will:
- Consolidate all job descriptions from today
- Analyze requirements and improve portfolio
- Commit and push changes to GitHub

## Usage Options

### Skip Steps
If you've already consolidated or don't want to push:

```bash
# Skip consolidation (already done)
python workflow_daily.py --skip-consolidate

# Skip portfolio improvement
python workflow_daily.py --skip-improve

# Skip GitHub push
python workflow_daily.py --skip-push
```

### Process Specific Date
```bash
# Process jobs from a specific date
python workflow_daily.py --date 20251216
```

### Push Only
```bash
# Only push existing changes to GitHub
python workflow_daily.py --push-only
```

### Run Only Specific Steps
```bash
# Only consolidate (skip improve and push)
python workflow_daily.py --skip-improve --skip-push

# Only improve portfolio (skip consolidate and push)
python workflow_daily.py --skip-consolidate --skip-push
```

## Workflow Steps

### Step 1: Consolidation
- Reads `all excels/quant_jobs_catalog.csv`
- Filters jobs posted today
- Creates:
  - `consolidated_jds_YYYYMMDD.md` - Markdown document
  - `today_jobs_summary_YYYYMMDD.csv` - CSV summary

### Step 2: Portfolio Improvement
- Reads consolidated CSV
- Extracts requirements using AI
- Identifies gaps in portfolio
- Generates new modules/files
- Commits changes to git

### Step 3: GitHub Push
- Pushes committed changes to remote repository
- Only pushes if there are new commits

## Error Handling

The workflow continues even if individual steps fail:
- Failed consolidation → Warning, but continues
- Failed improvement → Warning, but continues
- Failed push → Warning, workflow completes

Check the output for detailed error messages.

## Automation

### Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., Daily at 6:00 PM)
4. Action: Start a program
5. Program: `python`
6. Arguments: `workflow_daily.py`
7. Start in: `G:\My Drive\fuck_u_cunt\quant_scraper`

### Linux/Mac Cron
```bash
# Edit crontab
crontab -e

# Add daily at 6 PM
0 18 * * * cd /path/to/quant_scraper && python workflow_daily.py
```

## Prerequisites

1. **Job Catalog**: Must have `all excels/quant_jobs_catalog.csv` with today's jobs
2. **Portfolio Repo**: Configure `quant_poc_repo_path` in `config/settings.py`
3. **GitHub**: Configure `quant_poc_repo_remote` and `github_token` for auto-push

## Troubleshooting

### "Consolidated CSV not found"
- Run `consolidate_today_jds.py` first
- Or check if jobs were cataloged today

### "Portfolio repository path does not exist"
- Set `quant_poc_repo_path` in `config/settings.py`
- Ensure the path is correct

### "Git push failed"
- Check GitHub token in `config/secrets.py`
- Verify remote repository URL
- Check git credentials

## Related Scripts

- `consolidate_today_jds.py` - Standalone consolidation
- `improve_portfolio_from_today.py` - Standalone improvement
- `runAiBot.py` - Catalog new jobs from LinkedIn
