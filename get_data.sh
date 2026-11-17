#!/usr/bin/env bash
# Download the public Indian apparel e-commerce sales dataset (Amazon.in order report, Mar-Jun 2022).
# Original source: Kaggle "E-Commerce Sales Dataset" (thedevastator); this script uses a public GitHub copy.
set -e
mkdir -p data
curl -L --fail -o data/amazon_sale_report.csv \
  "https://raw.githubusercontent.com/AKSUF/ecommerce/223bbfe753a39f5911fb6a1314abc73a8c4563cb/archive/Amazon%20Sale%20Report.csv"
echo "ac9a366da5f3af418831fa53da9eebfc3b3838803e3774eec97dbcb291441beb  data/amazon_sale_report.csv" | sha256sum -c -
