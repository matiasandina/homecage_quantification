#' This function creates the lineplot 
#' It will try to handle datetime, ZT and hours from lights-on on the x axis
#' It will display the shading proper to lights on/off
#' @param df `data.frame` with datetime and movement values to plot
#' @param x_axis character to switch the x-axis. Values accepted are "datetime", "ZT", and "Hours from lights-on"
#' TODO: This needs to get properly replaced 
lineplot <- function(df, x_axis){
  
  # Theme for graphs
  
  theme_lineplot <- cowplot::theme_half_open() +
    theme(legend.position = "bottom",
          panel.grid = element_blank()) 
  
  
  
  x_lab <- case_when(x_axis == "datetime" ~ "Clock Time",
                     x_axis == "ZT" ~ "ZT",
                     x_axis == "Hours from lights-on" ~ "Hours from lights-on")
  
  p <- switch(x_axis,
              "datetime" = ggplot(df, aes(datetime, movement, group=mac, color=mac))+
                light_shade(df, mode="datetime") +
                scale_x_datetime(breaks = "2 hour",
                                 date_labels = "%H:%M"),
              "ZT" = ggplot(df, aes(zt, movement, group=mac, color=mac))+
                light_shade(df, mode = "zt") +
                scale_x_datetime(breaks = "2 hour",
                                 date_labels = "%H:%M"),
              "Hours from lights-on" = ggplot(df, aes(as.POSIXct(light_hours), movement, group=mac, color=mac))+
                scale_x_datetime(breaks= "2 hour",
                                 date_labels = "%H:%M")+
                annotate("rect",
                         xmin = as.POSIXct(data.table::as.ITime("12:00:00")),
                         xmax = as.POSIXct(data.table::as.ITime("23:59:59")),
                         ymin = -Inf, ymax = Inf,
                         alpha = 0.2, fill = "gray50")
  )
  
  p +
    geom_line()  +
    labs(title = "Movement", x = x_lab) +
    theme_lineplot -> p
  return(p)
  
}
