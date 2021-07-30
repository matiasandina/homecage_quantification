#' This function is trying to get the shading to provide to ggplot
#' TODO: make better using `make_lights.R` from fed quant
light_shade <- function(df, mode="datetime"){
  
  # let's build this summary for later parsing dates
  # and returning proper format
  df_on <- df %>%
    # just in case we have more than one day
    mutate(day = date(datetime)) %>%
    group_by(day) %>%
    mutate(min_datetime = min(datetime),
           max_datetime = max(datetime),
           min_zt = min(zt),
           max_zt = max(zt)) %>% 
    filter(lights=="lights-on") %>%
    summarise(min_datetime = unique(min_datetime),
              max_datetime = unique(max_datetime),
              min_zt = unique(min_zt),
              max_zt = unique(max_zt),
              first_dt_on = first(datetime),
              last_dt_on = last(datetime),
              first_zt_on = first(zt),
              last_zt_on = last(zt)
    ) 
  
  #View(df_on)
  
  switch(mode,
         # annotate in two layers
         # to do so, we cant `+`, we put them in a list
         "datetime" = list(
           annotate("rect",
                    xmin = df_on$min_datetime,
                    xmax = df_on$first_dt_on,
                    ymin = -Inf, ymax = Inf,
                    alpha = 0.2, fill = "gray50"),
           annotate("rect",
                    xmin = df_on$last_dt_on,
                    xmax = df_on$max_datetime,
                    ymin = -Inf, ymax = Inf,
                    alpha = 0.2, fill = "gray50")
         ),
         "zt" = annotate("rect",
                         xmin= df_on$last_zt_on,
                         xmax = df_on$max_datetime,
                         ymin = -Inf, ymax = Inf,
                         alpha = 0.2, fill = "gray50")
  )
  
}