USE online_retail;

-- 1. Dataset size
SELECT COUNT(*) AS total_records
FROM raw_invoice_lines;

-- 2. Positive sales by country
SELECT
    Country,
    ROUND(SUM(Quantity * UnitPrice), 2) AS sales
FROM raw_invoice_lines
WHERE Quantity > 0
  AND UnitPrice > 0
  AND InvoiceNo NOT LIKE 'C%'
GROUP BY Country
ORDER BY sales DESC
LIMIT 10;

-- 3. Monthly sales
SELECT
    DATE_FORMAT(InvoiceDate, '%Y-%m') AS sales_month,
    ROUND(SUM(Quantity * UnitPrice), 2) AS monthly_sales
FROM raw_invoice_lines
WHERE Quantity > 0
  AND UnitPrice > 0
  AND InvoiceNo NOT LIKE 'C%'
GROUP BY DATE_FORMAT(InvoiceDate, '%Y-%m')
ORDER BY sales_month;

-- 4. Customer RFM results
SELECT *
FROM customer_rfm
ORDER BY monetary_value DESC
LIMIT 10;
