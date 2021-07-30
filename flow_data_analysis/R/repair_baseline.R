#' @description This function detects the baseline of a signal using provided quantile
#' @details 
#' It will calculate the mean of the values on the quantile determined by `quant` parameter and subtract that to the input values
#' @param x numeric signal to calculate the baseline
#' @param quant probability threshold to provide to `quantile` function. Default is 0.05 (5% of values on x)
#' @return signal minus baseline
#' @seealso `quantile()`

repair_baseline <- function(x, quant=0.05){
  # we take the 0.1 quantile as the lowest values
  base <- mean(x[x < quantile(x, quant)])
  # we return x - base
  return(x - base)
}
