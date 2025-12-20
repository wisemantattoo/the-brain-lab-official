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
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y imagemagick
          # השורה הבאה מתקנת את הבעיה האדומה:
          sudo sed -i 's/<policy domain="path" rights="none" pattern="@\*"//g' /etc/ImageMagick-6/policy.xml
          pip install -r requirements.txt
      - name: Run Bot
        run: python main.py
