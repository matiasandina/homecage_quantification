#' This function returns the median filter of a signal
#' It will approximate NAs at the edges
#' @param x numeric vector for signal trying to filter
#' 

median_filter <- function(x){
  x <- runmed(x, 11, na.action = "na.omit", endrule = "keep")
  # this is to fill NAs 
  # do not remove na values when approx
  # if the NA are at the edges extend the closest values
  x <- zoo::na.approx(x, na.rm=F, rule=2)
  return(x)
}
