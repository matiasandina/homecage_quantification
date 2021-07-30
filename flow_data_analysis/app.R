library(shiny)
library(tidyverse)
library(dtplyr)
library(lubridate)
library(shinycssloaders)
library(shinyFiles)

# Helper functions --------------------------------------------------------
source("/home/choilab/homecage_quantification/flow_data_analysis/R/median_filter.R")
source("/home/choilab/homecage_quantification/flow_data_analysis/R/aggregate_data.R")
source("/home/choilab/homecage_quantification/flow_data_analysis/R/add_extra.R")
source("/home/choilab/homecage_quantification/flow_data_analysis/R/read_config_files.R")
source("/home/choilab/homecage_quantification/flow_data_analysis/R/match_by_group_date.R")
source("/home/choilab/homecage_quantification/flow_data_analysis/R/lineplot.R")
source("/home/choilab/homecage_quantification/flow_data_analysis/R/make_heatmap.R")
source("/home/choilab/homecage_quantification/flow_data_analysis/R/light_shade.R")
source("/home/choilab/homecage_quantification/flow_data_analysis/R/repair_baseline.R")
source("/home/choilab/homecage_quantification/flow_data_analysis/R/between_times.R")

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

        
        # clean and smooth -----
        print("Smoothing with median filter")
        df <- df %>% 
            group_by(filename) %>%
            # remove first movement value (it's zero and will mess up the baseline)
            slice(-1) %>% 
            # convert to NA values that are too big,
            # we will have a few extreme values when we have shifts from night to dark mode
            mutate(movement = ifelse(movement > 2e05, NA, movement),
                   movement = zoo::na.approx(movement, na.rm=F, rule=2)) %>% 
            # interpolated xy
            mutate(i_x = median_filter(x),
                   i_y = median_filter(y)) %>% 
            ungroup() 
        
        print("Smoothing baseline")
        df <- df %>% 
            mutate(lights_on = between_times(datetime, lights_on, lights_off)) %>% 
            group_by(filename, lights_on) %>% 
            mutate(movement = repair_baseline(movement)) %>% 
            select(-lights_on)
            
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
                     sum_df <- add_extra(sum_df, lights_on, lights_off)
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


