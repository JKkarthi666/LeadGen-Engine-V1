# 🛻 Caravan Listing Scraper

This project is a powerful and automated web scraper built with **Python** and **Selenium**. It scrapes detailed caravan listings from [Snowy River Perth](https://snowyriverperth.com.au/in-stock/) including title, prices, specifications, description, upgrades, and accordion-based technical details. The results are saved to an Excel spreadsheet.

---

## 🚀 Features

- Scrapes **multiple product URLs** from the stock page
- Extracts:
  - Product title
  - Model number
  - Prices (Retail, Tow-Away, Weekly)
  - Description and upgrade options
  - Key specifications
  - Primary and secondary images
  - All expandable accordion sections
- Simulates **human behavior** (random scrolling and clicks) to avoid detection
- Saves output into a clean `.xlsx` Excel file

---

## 📁 Output

The script generates:

- `caravan_data.xlsx` — A spreadsheet containing all collected caravan information

---

## 🛠️ Requirements

Make sure you have Python installed (>=3.7), then install the dependencies:

```bash
pip install -r requirements.txt
