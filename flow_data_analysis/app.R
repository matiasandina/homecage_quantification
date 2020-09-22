library(shiny)
library(tidyverse)
library(dtplyr)
library(lubridate)
library(shinycssloaders)
library(shinyFiles)

# Helper functions --------------------------------------------------------
# data analysis
median_filter <- function(x){
    x <- runmed(x, 11, na.action = "na.omit", endrule = "keep")
    # this is to fill NAs 
    # do not remove na values when approx
    # if the NA are at the edges extend the closest values
    x <- zoo::na.approx(x, na.rm=F, rule=2)
    return(x)
}

# data bin 
aggregate_data <- function(df, interval) {
    df %>% 
        mutate(datetime = cut(datetime, interval)) %>% 
        group_by(filename, datetime) %>% 
        summarise (
            movement = mean(movement),
            x = first(x),
            y = first(y),
            i_x = first(i_x),
            i_y = first(i_y)) %>% 
        ungroup()
}


# add extra layers to data 
add_extra <- function(df) {
    mac_pattern <- "[:alnum:]{2}:[:alnum:]{2}:[:alnum:]{2}:[:alnum:]{2}:[:alnum:]{2}:[:alnum:]{2}"
    
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


# Read config files -------------------------------------------------------

read_config_files <- function(target_date){
    dirs <- list.dirs(path = "/home/choilab/raspberry_IP/", recursive=FALSE)
    pattern_to_find <- paste0(target_date,".*_config.csv")
    files_inside <- lapply(dirs, function(tt) list.files(tt, pattern = pattern_to_find, full.names=TRUE)) %>%
        unlist()
    col_classes <- cols(
        mac = col_character(),
        date = col_character(),
        ID = col_character(),
        Treatment = col_character(),
        Dose = col_character(),
        Comment = col_character()
    )
    configs <- purrr::map(files_inside, function(x) read_csv(x, col_types = col_classes)) %>% bind_rows() 
    if (nrow(configs) > 0) {
        configs <- configs %>% rename(datetime = date)
    }
    return(configs)
}


# Match configs with data -------------------------------------------------


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



# Functions to make plots -------------------------------------------------

lineplot <- function(df, x_axis){
    
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

# Themes for graphs

theme_lineplot <- cowplot::theme_half_open() +
    theme(legend.position = "bottom",
          panel.grid = element_blank()) 

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

# time bins
time_bins <- c("10 sec", "1 min", "5 min")
names(time_bins) <- time_bins

# lights on
lights_on <- parse_time("07:00:00")
lights_off <- parse_time("19:00:00")

lights_on_sec <- seconds(lights_on)
lights_off_sec <- seconds(lights_off)


# Define UI --------------------------------------------------
ui <- fluidPage(
    # Application title
    titlePanel("Flow Data Analysis"),
    
    # Sidebar with a slider input for number of bins 
    sidebarLayout(
    sidebarPanel(
        h5(strong("Status")),
        textOutput(outputId = "status"),
        h5(strong("Select Data origin")),
        h5("Using the controls below, you can select to use previously aggregated data or upload pooled data for a new experiment."),
        hr(),
        shinyDirButton("directory", "Choose Directory", "Choose the directory of previously aggregated data", viewtype = "detail",
                         icon = icon("folder")),
        shinyFilesButton("file", "Upload .csv.gz", "Upload .csv.gz", multiple = TRUE, viewtype = "detail",
                         icon = icon("file")),
        tags$hr(),
        #tags$h4("The output of a folder selection"),
        tags$p(HTML("All data will go into the selected root directory.")),
        verbatimTextOutput("directorypath"),
        tags$p(HTML("You are currently working with this file(s):")),
        verbatimTextOutput("filepaths"),
        #fileInput("file", "Data", buttonLabel = "Upload .csv.gz", multiple = TRUE),
    ),
    
    # Show a plot of the generated distribution
    mainPanel(
        tabsetPanel(
                tabPanel("Data", value = "data",
                         column(12,
                                h4("Data"), 
                                #h5("Showing 10 first lines"),
                                # DT creating errors
                                #DT::dataTableOutput("preview1"))
                                tableOutput("preview1"))
                         ),
                # TabPanel Individual ------------
                tabPanel("Individual", value = "individual",
                         h3("Homecage Movement"),
                         fluidRow(
                             column(4,
                         radioButtons("individual_radio", label = h4("Show Data Aggregated by"),
                                      choices = time_bins,
                                      # no default
                                      selected = character(0)),
                         textOutput(outputId = "individual_status"),
                         ),
                             column(4,
                         radioButtons("time_radio", label = h4("Display time type"),
                                      choices = c("datetime", "ZT", "Hours from lights-on"),
                                      # no default
                                      selected = character(0))
                             ),
                            column(4,
                                   selectInput('datein', 'Filter Dates', state.name, multiple=TRUE, selectize=TRUE)
                            )
                         ),
                         hr(),    
                         plotOutput("individual_plot") %>% withSpinner(color="#0dc5c1"),
                         hr(),
                         fluidRow(column(width=4, 
                                         downloadButton("download_individual_plot",
                                               label = "Download plot",
                                               class = "btn-block")
                                         )),
                         h3("Homecage Position Heatmap"),
                         hr(),    
                         plotOutput("heatmap_plot") %>% withSpinner(color="#0dc5c1"),
                         hr(),
                         fluidRow(column(width=4, 
                                downloadButton("download_heatmap_plot",
                                               label = "Download plot",
                                               class = "btn-block")
                                 ))
                         ),
                # TabPanel Grouped ------------
                tabPanel("Grouped", value = "grouped",
                         plotOutput("grouped_plot") %>% withSpinner(color="#0dc5c1")
                         )
        
                    )
    )
)
)

# Define server ----------------------------------------------
server <- function(input, output, session) {
    # set Max file to 10 Gb
    options(shiny.maxRequestSize = 10000*1024^2)
    
    # Reactive values
    values <- reactiveValues(datasource = "")
    
    output$status <- renderText("Waiting for Data")
    
    # Choosing dir/files
    volumes <- c(Home = fs::path_home(), "R Installation" = R.home(), getVolumes()())
    shinyDirChoose(input, "directory", roots = volumes,
                   session = session, restrictions = system.file(package = "base"))
    shinyFileChoose(input, "file", roots = volumes, session = session)
    
    # Upload ---------------------------------------------------------------
    
    get_paths <- reactive({
        req(values$datasource != "")
        # handle states
        if (values$datasource == "prev_calc") {
            # this will be a directory
            file_path <- parseDirPath(volumes, input$directory)
            return(file_path)
        }
        if (values$datasource == "upload") {
                # get the path
                file_path  <- parseFilePaths(volumes, input$file)$datapath
                # make the directory root path appear on directorypath
                output$directorypath <- renderPrint(dirname(file_path))
                return(file_path)
        }
    })

    # directory input -------------
    observeEvent(input$directory,
        {
        # print the dir  
        output$directorypath <- renderPrint({
            if (is.integer(input$directory)) {
                cat("No directory has been selected yet")
            } else {
                parseDirPath(volumes, input$directory)
            }
        })
        if (!is.integer(input$directory)) {
            files_in_dir <- list.files(parseDirPath(volumes, input$directory),
                                       pattern = "_aggregate_")
            if (identical(files_in_dir, character(0))) {
                showNotification("No aggregate files in chosen directory. Please choose another one", 
                                 duration = 30, type = "error")
                
            } else {
                # update the status to previous calculation
                values$datasource <- "prev_calc"
            }
            }
        # print(values$datasource == "prev_calc")
        }
    )
    
    # file input ---------------
    observeEvent(input$file,
                 {
                     if (!is.integer(input$file)) {
                         values$datasource <- "upload" 
                         # call function to tidy data
                         tidied()
                     }
                 })
    
    ## print to browser
    output$filepaths <- renderPrint({
        if (is.integer(input$file)) {
            cat("No files have been selected")
            # do nothing
        } else {
            # print(input$file$datapath)
            get_paths()
        }
    })
    
    raw <- reactive({
        req(is.integer(input$file) == FALSE)
        #print(input$file)
        #stop()
        output$status <- renderText("Reading")
        #delim <- if (input$delim == "") NULL else input$delim
        # we leave as NULL to guess
        delim <- NULL

        # col classes
        flow_classes <-  cols(
            filename = col_character(),
            datetime = col_datetime(),
            movement = col_double(),
            x = col_double(),
            y = col_double()
        )

        files_to_read <- get_paths()
        print(files_to_read)

        # read and interpolate
        li <- lapply(files_to_read,
                     function(tt)
                        vroom::vroom(tt, delim = delim, skip = 0, col_types = flow_classes)
                     # TODO: throw errors if the names do not match here
        )
        print(sapply(li, names))
        names(li) <- files_to_read
        output$status <- renderText("Reading Finished")
        return(li)
    })
    
    
    # Clean ----------------------------------------------------------------
    tidied <- reactive({
        
        req(is.integer(input$file) == FALSE && values$datasource == "upload")
        # user feedback ----
        output$status <- renderText("Cleaning Data")
        print("Cleaning Data...")
        showModal(modalDialog("Cleaning data... Please wait.", easyClose = FALSE))
        # get raw data
        li <- raw()
        # code for a plot
        df <- bind_rows(li) 

        
        # clean -----
        print("Smoothing with median filter")
        df <- df %>% 
            group_by(filename) %>%
            # interpolated xy
            mutate(i_x = median_filter(x),
                   i_y = median_filter(y)) %>% 
            ungroup() 
        
        print(df[nrow(df), "filename"])

        removeModal()
        showModal(modalDialog("Aggregating and writing data... Please wait.", easyClose = FALSE))
        
        # we make a new folder with the same name of the root directory
        # we asume experiments will be put in that folder if they belong there
        # of more than one, we keep the first one
        root <- dirname(get_paths())[1]
        root <- file.path(root, basename(root))
        print("Creating folder at")
        print(root)
        dir.create(root)
        purrr::map(time_bins, function(bin) {
            filename <- paste0(basename(root), "_aggregate_",
                               str_replace(string = bin, " ", "_"),
                               ".csv.gz")
            filename <- file.path(root, filename)

                vroom::vroom_write(df %>%
                                        aggregate_data(interval = bin),
                                   path = filename)
            print(paste("writing", filename))
            
                }
                )
        # filter dates 
        #filter_dates <- get_date_range()
        #df <- df %>%
        #    filter(between(date, filter_dates$from, filter_dates$to)) %>%
        #    mutate(date = lubridate::as_datetime(date))
        
        removeModal()
        output$status <- renderText("Cleaning Finished")
        print("Cleaning Finished")
        return(df)
    })
    
    # Table Outputs -----------------------
    
    table_render_options <- list(pageLength = 5,
                                 lengthMenu = list(c(5, 15, -1),
                                                   list('5', '15', 'All'))
    )
    
    # data too big, only showing first 100 rows
    #output$preview1 <- DT::renderDataTable(tidied() %>%  slice(1:10),
    #                                   options = table_render_options)
    
    #output$preview1 <- renderTable(tidied()[1:10, ])

    # individual plot ---------------------------------------------------------
    read_aggregate_data <- function(bin_pattern){
        print(values$datasource)
        print(is.integer(input$file))
        req(is.integer(input$file) == FALSE | values$datasource == "prev_calc")
        # this will break if get_paths is a multiple thing
        # we could check that the root folder is unique
        root <- dirname(get_paths())
        root <- file.path(root, basename(root))
        # there should be only one here...
        file <- list.files(path = root, pattern = bin_pattern, full.names = TRUE)
        print(paste("Trying to read aggregate with", bin_pattern))
        print(file)
        df <- vroom::vroom(file)
        return(df)
    }
    

    # Feedback for radio buttons individual plot -------------------------------------------
    output$individual_status <- renderText(
        validate(
            need(input$individual_radio != character(0), message = "Please select sampling frequency"),
            need(input$time_radio != character(0), message = "Please select x axis time type")
        )
    )
    

    #  Observe radio buttons individual plot ----------------------------------
    observeEvent({
        input$individual_radio
        input$time_radio}
        ,
                 {
                     output$individual_status <- renderText("")
                     # parse the individual_radio ----
                     bin_pattern <- str_replace(input$individual_radio, " ", "_")
                     # call the reactive function
                     sum_df <- read_aggregate_data(bin_pattern)
                     # add the extra info layers
                     sum_df <- add_extra(sum_df)
                     # go get the config files
                     target_dates <- sum_df %>%
                         mutate(datetime = str_extract(string = datetime,
                                                       pattern = "[0-9]{4}-[0-9]{2}-[0-9]{2}")) %>%
                         pull(datetime) %>% unique()
                     # update date selector
                     updateSelectInput(session = session, inputId = "datein",
                                       choices = target_dates)
                     configs <- purrr::map(target_dates, read_config_files) %>% bind_rows()
                     # bind 
                     sum_df <- match_by_group_date(sum_df, configs, mac, datetime)
                     print(sum_df)

                     # call the plot
                     output$individual_plot <- renderPlot(lineplot(sum_df, x_axis = input$time_radio))
                     output$heatmap_plot <- renderPlot(make_heatmap(sum_df))

    })
    

    # Observe date filtering individual ---------------------------------------
    observeEvent(
        input$datein,{
        output$individual_status <- renderText("")
        # parse the individual_radio ----
        bin_pattern <- str_replace(input$individual_radio, " ", "_")
        # call the reactive function
        sum_df <- read_aggregate_data(bin_pattern)
        # add the extra info layers
        sum_df <- add_extra(sum_df)
        # go get the config files
        target_dates <- sum_df %>%
            mutate(datetime = str_extract(string = datetime,
                                          pattern = "[0-9]{4}-[0-9]{2}-[0-9]{2}")) %>%
            pull(datetime) %>% unique()
        configs <- purrr::map(target_dates, read_config_files) %>% bind_rows()
        # bind 
        sum_df <- match_by_group_date(sum_df, configs, mac, datetime)
        # Filter date
        if (!is.null(input$datein)){
            sum_df <- filter(sum_df, str_detect(string = lubridate::date(datetime),
                                                pattern = paste(input$datein, collapse="|")))
        }
        # call the plot
        output$individual_plot <- renderPlot(lineplot(sum_df, x_axis = input$time_radio))
        output$heatmap_plot <- renderPlot(make_heatmap(sum_df))
        
        })

    

    # Download plots ----------------------------------------------------------
    output$download_individual_plot = downloadHandler(
        # do we need this ?
        # decide which plot to save 
        #  plot_to save <- case_when(input$tabs == ...)
        filename = function() {"plot.svg"},
        content = function(file) {
            ggsave(file, device = "svg", width=11, height=8.5)
            
        }
    )

}

# Run the application 
shinyApp(ui = ui, server = server)


