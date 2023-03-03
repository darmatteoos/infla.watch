library(tidyverse)
library(jsonlite)

prod_df <- fromJSON("R_formatted_data/R_all_products_no_deals_01_03_2023_10_51.json", simplifyDataFrame = TRUE)
prod_df <- as_tibble(prod_df)

