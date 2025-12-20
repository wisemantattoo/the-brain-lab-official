name: Daily Video Bot
on:
  schedule:
    - cron: '0 10 * * *'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install System Dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y imagemagick fonts-liberation
          sudo sed -i 's/rights="none" pattern="@\*"/rights="read|write" pattern="@\*"/g' /etc/ImageMagick-6/policy.xml
      - name: Install Python Dependencies
        run: pip install -r requirements.txt
      - name: Run Bot
        env:
          CLIENT_SECRET_JSON: ${{ secrets.CLIENT_SECRET_JSON }}
          YOUTUBE_CODE: ${{ secrets.YOUTUBE_CODE }}
        run: python main.py
