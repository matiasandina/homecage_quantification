#' This function averages data using a time bin interval
#' It is a wrapper for the `cut` function but applied to a `data.frame`.
#' It will calculate the mean for the `movement` column on `df`.
#' It will take the first positions on `xy` vectors.
#' @param df `data.frame` to aggregate by `interval`
#' @param interval character vector of the time bin to provide to `cut` base function (e.g., "5 min")
aggregate_data <- function(df, interval) {
  df %>% 
    mutate(datetime_bin = cut(datetime, interval)) %>% 
    group_by(filename, datetime_bin) %>% 
    summarise (
      movement = mean(movement),
      x = first(x),
      y = first(y),
      i_x = first(i_x),
      i_y = first(i_y)) %>% 
    ungroup()
}
