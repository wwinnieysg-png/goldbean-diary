name: Update Hong Kong gold prices
on:
  workflow_dispatch:
  schedule:
    - cron: '15 2,6,11 * * *'
permissions:
  contents: write
concurrency:
  group: gold-prices
  cancel-in-progress: false
jobs:
  update:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python -m pip install beautifulsoup4==4.13.4
      - run: python update-gold-prices.py
      - name: Publish public quote JSON
        run: |
          git config user.name 'github-actions[bot]'
          git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
          git add gold-prices.json
          if git diff --cached --quiet; then exit 0; fi
          git commit -m 'Update Hong Kong gold buyback quotes'
          git pull --rebase origin main
          git push origin HEAD:main
