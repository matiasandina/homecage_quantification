#' This function adds extra layers to data
#' The idea is that we do computation instead of saving columns that can be regenerated.
#' It will get the MAC address pattern from the filename
#' It will add 
#' It will add the lights-on/off
#' @param df data.frame from movement as calculated by the app
#' @param lights_on hms of the lights-on (e.g., "07:00:00") 
#' @param lights_off hms of the lights-on (e.g., "19:00:00") 

add_extra <- function(df, lights_on, lights_off) {
  mac_pattern <- "[:alnum:]{2}:[:alnum:]{2}:[:alnum:]{2}:[:alnum:]{2}:[:alnum:]{2}:[:alnum:]{2}"
  # we need this to calculate zt
  lights_on_sec <- lubridate::seconds(lights_on)

  df <- df %>% 
    mutate(
      # assign mac
      mac = str_extract(filename,
                        pattern = mac_pattern),
      # make shift to ZT
      time = data.table::as.ITime(datetime),
      zt = datetime - lights_on_sec,
      light_hours = time - data.table::as.ITime(lights_on),
      # make condition
      lights = factor(ifelse(between(time, lights_on, lights_off),
                             "lights-on", "lights-off"),
                      levels = c("lights-on", "lights-off"))
    )
  return(df)
}
