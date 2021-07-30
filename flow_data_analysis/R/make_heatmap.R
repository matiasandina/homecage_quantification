#' This function makes heatmaps from the data of the app
make_heatmap <- function(df){
  
  p <- ggplot(df %>% mutate(day = lubridate::date(datetime)),
              aes(i_x, i_y)) +
    # If you want to make sure the peak intensity is the same in each facet,
    # use `contour_var = "ndensity"`.
    geom_density_2d_filled(contour_var = "ndensity") +
    #   geom_path(alpha=0.1, color="white") +
    facet_grid(day~mac)+
    theme_void()+
    theme(legend.position="bottom")+
    # add the box limits (somewhat by eye from clean_cage_snapshot.png)
    annotate("rect", xmin=20, xmax=500, ymin=0, ymax=480, lwd=1, fill=NA, color="red")
  coord_cartesian(xlim=c(0,640), ylim=c(0,480))
  return(p)
}
