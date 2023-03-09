library(tidyverse)
library(jsonlite)

prod_df_V0 <- fromJSON("R_formatted_data/R_all_products_no_deals_V0_04_03_2023_09_10.json", simplifyDataFrame = TRUE)
prod_df_V0 <- as_tibble(prod_df_V0)

# fresh_prod <- prod_df_V0 |> 
#   filter(qty > 0) |> 
#   filter(fresh == TRUE)
# 
# pane <- prod_df_V0 |> 
#   filter(qty > 0) |> 
#   filter(grepl("[Pp]ane", name))

###### REQUIRES import_json.R

only_natura <- data |> 
  filter(grepl("NaturaSì", brand))

data |>
  filter(sku == "000100002890") |>
  arrange(date) |>
  ggplot(aes(x = date, y = price)) +
  geom_line()

data |> 
  group_by(sku) |> 
  summarize(price_var = n_distinct(price)) |> 
  arrange(desc(price_var))

data |>
  filter(sku == "000100002890")
