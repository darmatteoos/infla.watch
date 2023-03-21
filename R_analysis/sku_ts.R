library(tidyverse)
library(jsonlite)

source("import_json.R")

#converting to a simpler date format for comparisons and excluding
#unecessary qty
data <- data |> 
  mutate(date = as.Date(date, format = "%Y-%m-%d")) |> 
  select(-c(qty))

#removing duplicates (data is malformed especially on 03-04-2023 - fixed)
data <- data |> 
  distinct()

#filtering by two dates to compare between them, without taking into account
#the data that isn't comprised of both, then removes the row used for filtering
data <- data |>
  filter(date %in% c(as.Date('2023-02-01'),as.Date('2023-03-01'))) |>
  group_by(sku) |>
  mutate(n = n()) |>
  filter(n == 2) |>
  select(-c(n))

#adding on the same row both the price of the first and second date, 
#for comparison purposes, using id_cols with the unique identifier (sku)
#to avoid renaming, rebranding or changes to the package information to 
#give duplicate rows (see further down for examples). This means that
#any meaningful information for plotting must be derived from earlier data
price_comparison <- data |>
  pivot_wider(
    id_cols = c("sku"),
    names_from = date, 
    values_from = price
    )

#some skus that don't seem to be converted by pivot_wider w/o id_cols:
# sku         
# <chr>       
#   1 000100042838
# 2 000100059557
# 3 000100043846
# 4 000100061737
# 5 000100043848
# 6 000100043847
# 7 000100043849
# 8 000100021314
# 9 000100059550
# 10 000100066312
# 11 000100029223
  
price_comparison <- price_comparison |>
  ungroup() |> 
  rename(
    before = `2023-02-01`,
    after = `2023-03-01`
    ) |> 
  mutate(
    price_delta = (after - before),
    has_risen = (before < after),
    has_lowered = (before > after),
    is_equal = (before == after)
  )

price_comparison <- price_comparison |> 
  mutate(
    price = ifelse(
      before == after,
      "is_equal",
      ifelse(
        before <= after,
        "has_risen",
        "has_lowered"
      )
    )
  ) |> 
  select(-c(before:is_equal))

price_comparison |>
  count(price) |>
  ggplot(
    mapping = aes(x = price, y = n, fill = price),
    title = "prova"
  ) +
  geom_col() + 
  labs(
    title = "Products price comparison between 2023-02-01 and 2023-03-01",
    x = "",
    y = "count"
  )




price_comparison |>
  filter(price_delta > 0 & price_delta < 10) |> 
  ggplot(aes(x = price_delta)) +
  geom_histogram(binwidth = 0.1)


#filtering for just the products with brand "NaturaSì" and
#that are present in each date observation
perc_data <- data |> 
  group_by(sku) |> 
  mutate(n = n()) |>
  ungroup() |> 
  filter(n == max(n)) |> 
  select(-c(n))

perc_data <- perc_data |>
  select(date, sku, price) |> 
  pivot_wider(
    values_from = price,
    names_from = date
  )

perc_data <- perc_data |> 
  pivot_longer(
    cols = matches("2023")&(!matches("2023-01-29")),
    names_to = "date",
    values_to = "price"
  ) |>
  mutate(date = as.Date(date, format = "%Y-%m-%d")) |> 
  mutate(delta = (price-`2023-01-29`)/(`2023-01-29`)*100) |> 
  group_by(date) |> 
  summarize(
    mean_delta = mean(delta)
  ) |> 
  ungroup()

perc_data

perc_data |> 
  ggplot(aes(date, mean_delta)) +
  geom_line() + 
  labs(
    title = "NaturaSì index price change (%)",
    subtitle = "using 2023-01-31 data as benchmark",
    x = "Date",
    y = "% change"
  )


  


# perc_data %>% 
# mutate_at(vars(!(matches("2023-01-29")|matches("sku"))), )
  