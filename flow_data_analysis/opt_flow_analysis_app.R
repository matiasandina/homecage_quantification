library(tidyverse)
library(lubridate)

# fake data
df <- expand_grid(
#  filename = NA,
  mac = LETTERS[1:3],
  datetime = seq(parse_datetime("2020-06-12 00:00:00"),
                 parse_datetime("2020-06-12 23:59:00"), "1 min"),
) %>% 
  mutate(movement = rnorm(n = length(datetime), 0, 1))


# Themes for graphs

theme_lineplot <- cowplot::theme_half_open() +
  theme(legend.position = "bottom")

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
              ) %>%
    mutate_all(as.numeric)

  switch (mode,
    # annotate in two layers
    # to do so, we cant `+`, we put them in a list
    "datetime" = list(
      annotate("rect",
                          xmin= df_on$min_datetime,
                          xmax = df_on$first_dt_on,
                          ymin = -Inf, ymax = Inf,
                          alpha = 0.2, fill = "gray50"),
      annotate("rect",
                            xmin= df_on$last_dt_on,
                            xmax = df_on$max_datetime,
                            ymin = -Inf, ymax = Inf,
                            alpha = 0.2, fill = "gray50")
      ),
    "zt" = annotate("rect",
                    xmin= df_on$last_zt_on,
                    xmax = df_on$max_zt,
                    ymin = -Inf, ymax = Inf,
                    alpha = 0.2, fill = "gray50")
  )
  
}


# lights on
lights_on <- parse_time("07:00:00")
lights_off <- parse_time("19:00:00")

lights_on_sec <- seconds(lights_on)
lights_off_sec <- seconds(lights_off)

df <- df %>% 
  # make shift to ZT
  mutate(time = data.table::as.ITime(datetime),
         zt = datetime - lights_on_sec) %>% 
  # make condition
  mutate(lights = factor(ifelse(between(time, lights_on, lights_off),
                         "lights-on", "lights-off")),
         lights = fct_relevel(lights,
                              levels = c("lights-on", "lights-off"))
         )
# group mac is not awesome, look how we can do mouse_id instead
df %>% group_by(mac, lights) %>%
  summarise(mean_mov = mean(movement)) %>%
ggplot(aes(lights, mean_mov, group=mac, color=mac))+
  geom_line()+
  geom_point()+
  labs(x = "")+
  theme_lineplot


# lineplot -----
ggplot(df,
       aes(as.numeric(datetime), movement,
           group=mac, color=mac)) +
  light_shade(df)+
  geom_line()+
  theme_lineplot

ggplot(df,
       aes(as.numeric(zt), movement,
           group=mac, color=mac)) +
  light_shade(df,mode = "zt")+
  geom_line()+
  theme_lineplot



# actogram plot -------------

df %>%
  mutate(day = date(datetime),
         hours = floor_date(datetime, "1 hour")) %>%
  group_by(day, hours, mac) %>%
  summarise(movement = sum(movement)) %>%
  ggplot(aes(hours, mac, fill=movement))+
  geom_tile()
