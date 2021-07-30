# This is a wrapper to provide a logical filter for times
between_times <- function(datetime, lower, upper) {
  # TODO: enforce argument classes here
  # datetime has to be class POSIXct POSIXt
  # upper and lower have to be class "hms" 
  
  return(
  data.table::between(
    data.table::as.ITime(datetime),
    lower = lower,
    upper = upper)
  )
}