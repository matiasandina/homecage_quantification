#' This function binds the configs and the data using two keys.
#' It uses a group and datetime to bind the data.
#' Datetime binding will use the closest distance between datetimes
#' @param df1 `data.frame` to bind `df2`.
#' @param df2 `data.frame` to bind with `df1`.
#' @param grp column name present in both `df1` and `df2`. It will get intersected to provide the common binding
#' @param datecol coulumn name present in  
match_by_group_date <- function(df1, df2, grp, datecol) {
  
  grp1 <- df1 %>% pull({{grp}}) %>% unique()
  grp2 <- df2 %>% pull({{grp}}) %>% unique()
  
  li <-
    lapply(intersect(grp1, grp2), function(tt) {
      d1 <- filter(df1, {{grp}}== tt)
      d2 <- filter(df2, {{grp}}==tt) %>% mutate(indices = 1:n())
      d2_date <- d2 %>% pull({{datecol}}) %>% as.POSIXct()
      d1 <- mutate(d1, indices = map_dbl({{datecol}}, function(d) which.min(abs(d2_date - as.POSIXct(d)))))
      
      left_join(d1,d2, by=c(quo_name(enquo(grp)), "indices"))
    })
  
  # bind rows
  return(bind_rows(li) %>% rename(datetime = datetime.x, exp_start = datetime.y))
}
