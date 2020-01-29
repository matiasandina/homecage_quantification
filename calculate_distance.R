calculate_distance <- function(df){

# Helper function
euc.dist <- function(x1, x2) sqrt(sum((x1 - x2) ^ 2))

# Make space  
vec <- vector(mode="numeric", length = nrow(df))

message(sprintf("Calculating frame to frame velocity and distances for %s.",
                unique(df$animal_id)))

pb <- txtProgressBar(min = 0, max = nrow(df), style = 3)

# subset only once instead of in every iteration
position_points <- df[ , c("x", "y")]

 for (i in 2:nrow(df)){

  vec[i] <- euc.dist(position_points[i-1, ], position_points[i, ])
  
  setTxtProgressBar(pb, i)  
 } 

close(pb)

# append to df
df$velocity <- vec
df$distance <- cumsum(vec)

return(df)
  
}

