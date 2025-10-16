# ============================================================================
# CREATE SAMPLE SALES DATA FOR LESSON 8
# ============================================================================
# This creates a realistic sales dataset for practicing advanced wrangling

# Set seed for reproducibility
set.seed(123)

# Load the sales data from CSV
sales_data <- read_csv("raw/lesson8_sales_data.csv")

cat("✅ Sales data loaded successfully!\n")
cat("   Rows:", nrow(sales_data), "\n")
cat("   Date range:", min(sales_data$OrderDate), "to", max(sales_data$OrderDate), "\n\n")

cat("📊 Dataset Structure:\n")
cat("   • OrderID: Unique transaction identifier\n")
cat("   • OrderDate: Transaction date (Q1 2024)\n")
cat("   • Product: Laptop, Mouse, Keyboard, Monitor, Webcam, Headphones\n")
cat("   • Sales: Transaction amount ($)\n")
cat("   • Quantity: Number of items\n")
cat("   • Region: North, South, East, West\n")
cat("   • Category: Electronics, Peripherals\n")
cat("   • CustomerType: New, Returning, VIP\n\n")

cat("📋 First 10 rows:\n")
print(head(sales_data, 10))
