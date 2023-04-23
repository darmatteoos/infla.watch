#! /usr/local/bin/Rscript

library(renv)

# Restore packages for this project
renv::activate()

library(purrr)
library(tidyverse)
library(jsonlite)
library(DBI)
library(RPostgres)

first_time <- FALSE
path <- "data/to_transform"
files <- dir(path, pattern = "*.json")

# joining files in a single list (source:
# https://stackoverflow.com/questions/35421870/reading-multiple-json-files-in-a-directory-into-one-data-frame
# )
data <- files %>%
  map_df(~fromJSON(file.path(path, .), flatten = TRUE))

# time_data <- fromJSON(file = "../data/metadata.json")
# time_data <- as.data.frame(time_data)

#to convert a list to a tibble, we need to first pass through a df
data <- data.frame(data)
data <- as_tibble(data)

#converting character to posix
data$date <- as.POSIXct(data$date)

#erase rows with no price
data <- data |>
  filter(!is.na(price))

#order by date and use it as the first column
data <- data |>
  arrange(date) |>
  relocate(date, .before = sku)

#removing unnecessary columns to free up space
data <- data |>
  select(-c(qty))
data <- data |>
  select(-c(fresh:is_package))

#connecting to a amazon aws RDS instance...

user <- Sys.getenv("DB_USER")
host <- Sys.getenv("DB_HOST")
name <- Sys.getenv("DB_NAME")
port <- Sys.getenv("DB_PORT")
psw <- Sys.getenv("DB_PSW")

#or simply for testing purposes locally:
con <- DBI::dbConnect(
  RPostgres::Postgres(),
  dbname = name, #this is not the real name of db, but apparently this what has to be done (https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ConnectToPostgreSQLInstance.html#USER_ConnectToPostgreSQLInstance.Troubleshooting)
  host = host,
  port = port,
  user = user,
  password = psw
)

#...(running postresql) to
#write all the contents of the dataframe to (command meant to be run
#only once!!)...

# ...then connecting to the instance only to update it with daily
#fresh data.

# if (first_time == TRUE) {
#   dbWriteTable(con, "supermkts", data)
# } else {
#   dbWriteTable(con, "prices", data, append = T)
# }

data <- tbl(con, "prices")
data <- data |> 
  collect() |> 
  arrange(date) |> 
  slice(n())

print(data)

dbDisconnect(con)