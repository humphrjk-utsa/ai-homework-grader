# Lesson 7: String Manipulation and Date/Time Data

# Load necessary packages
library(tidyverse) # includes stringr
library(lubridate) # for date/time manipulation

# 1. String Manipulation with stringr

# Sample data with text strings
product_descriptions <- data.frame(
  ProductID = 1:5,
  Description = c(
    "Laptop Pro 15-inch, i7 processor, 16GB RAM",
    "Wireless Mouse, ergonomic design, black color",
    "Mechanical Keyboard RGB, gaming edition",
    "27-inch Monitor 4K, IPS panel, slim bezel",
    "USB-C Hub with HDMI, PD, and 3 USB 3.0 ports"
  )
)

print("Original Product Descriptions:")
print(product_descriptions)

# a) str_detect(): Detect patterns in strings
# Find products with "gaming" in their description
gaming_products <- product_descriptions %>%
  filter(str_detect(Description, "gaming"))
print("Gaming Products:")
print(gaming_products)

# Find products with "USB" (case-insensitive)
usb_products <- product_descriptions %>%
  filter(str_detect(Description, regex("usb", ignore_case = TRUE)))
print("USB Products (case-insensitive):")
print(usb_products)

# b) str_replace() / str_replace_all(): Replace patterns in strings
# Replace "inch" with "\""
cleaned_descriptions <- product_descriptions %>%
  mutate(Description_Clean = str_replace_all(Description, "inch", "\""))
print("Descriptions with \"inch\" replaced:")
print(cleaned_descriptions)

# Replace multiple spaces with a single space
text_with_extra_spaces <- "This   text has   extra   spaces."
cleaned_text <- str_replace_all(text_with_extra_spaces, "\\s+", " ")
print(paste("Cleaned text:", cleaned_text))

# c) str_to_lower() / str_to_upper() / str_to_title(): Change case
product_descriptions_case <- product_descriptions %>%
  mutate(
    Description_Lower = str_to_lower(Description),
    Description_Upper = str_to_upper(Description),
    Description_Title = str_to_title(Description)
  )
print("Descriptions with different cases:")
print(product_descriptions_case)

# d) str_subset(): Extract strings that match a pattern
only_laptops <- str_subset(product_descriptions$Description, "Laptop")
print("Only Laptop descriptions:")
print(only_laptops)

# e) str_extract() / str_extract_all(): Extract matching patterns
# Extract numbers (e.g., screen size, RAM)
numbers_extracted <- str_extract_all(product_descriptions$Description, "\\d+")
print("Numbers extracted from descriptions:")
print(numbers_extracted)

# 2. Working with Date and Time Data with lubridate

# Sample data with various date/time formats
order_data <- data.frame(
  OrderID = 1:5,
  OrderDate_str = c("2024-01-01", "02/15/2024", "Jan 20, 2024", "2024-03-10 14:30:00", "2024-04-05 09:00:00 UTC"),
  DeliveryDate_str = c("2024-01-05", "02/20/2024", NA, "2024-03-12 10:00:00", "2024-04-07 15:00:00 UTC")
)

print("Original Order Data with Date Strings:")
print(order_data)

# a) Converting to date/time formats
# ymd(): Year-Month-Day
order_data <- order_data %>%
  mutate(OrderDate_ymd = ymd(OrderDate_str))

# mdy(): Month-Day-Year
order_data <- order_data %>%
  mutate(OrderDate_mdy = mdy(OrderDate_str))

# ymd_hms(): Year-Month-Day Hour:Minute:Second
order_data <- order_data %>%
  mutate(OrderDateTime_hms = ymd_hms(OrderDate_str))

print("Order Data with Converted Dates:")
print(order_data)

# b) Extracting components (year, month, day, hour, minute, second)
order_data <- order_data %>%
  mutate(
    OrderYear = year(OrderDate_ymd),
    OrderMonth = month(OrderDate_ymd, label = TRUE, abbr = FALSE),
    OrderDay = day(OrderDate_ymd),
    OrderHour = hour(OrderDateTime_hms),
    OrderMinute = minute(OrderDateTime_hms)
  )
print("Order Data with Date Components Extracted:")
print(order_data)

# c) Calculating time differences
order_data <- order_data %>%
  mutate(
    DeliveryDate_ymd = ymd(DeliveryDate_str),
    DeliveryLeadTime_days = interval(OrderDate_ymd, DeliveryDate_ymd) / days(1)
  )
print("Order Data with Delivery Lead Time:")
print(order_data)

# Hands-on Exercise: Clean product descriptions and analyze order timestamps.
# Create a dummy dataset for the exercise
exercise_data <- data.frame(
  Item = c("Product A (New Version)", "Product B - Discontinued", "Product C (Limited Edition)"),
  LogTime = c("2024-05-01 10:00:00", "2024-05-01 11:30:00", "2024-05-02 09:15:00")
)

print("Exercise Data:")
print(exercise_data)

# Task 1: Remove "(New Version)", "- Discontinued", "(Limited Edition)" from the Item column.
# Task 2: Convert LogTime to a proper datetime object and extract the hour of the log.

# Solution (for instructor/self-check):
exercise_solution <- exercise_data %>%
  mutate(
    Item_Clean = str_replace_all(Item, "\\s*\\(New Version\\)|\\s*-\\s*Discontinued|\\s*\\(Limited Edition\\)", ""),
    LogDateTime = ymd_hms(LogTime),
    LogHour = hour(LogDateTime)
  )

print("Exercise Solution:")
print(exercise_solution)


