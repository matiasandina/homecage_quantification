library(shiny)
library(tidyverse)

# Define UI for application that draws a histogram
ui <- fluidPage(
    # Application title
    titlePanel("Flow Data Analysis"),
    
    # Sidebar with a slider input for number of bins 
    sidebarLayout(
    sidebarPanel(
        fileInput("file", "Data", buttonLabel = "Upload .csv", multiple = TRUE),
        dateRangeInput('dateRange',
                       label = 'Date range input: yyyy-mm-dd',
                       start = Sys.Date() - 2, end = Sys.Date() + 2
        )
    ),
    
    # Show a plot of the generated distribution
    mainPanel(
        tabsetPanel(
                tabPanel("Data", value = "data",
                         column(12,
                                h4("Raw Data"),
                                dataTableOutput("preview1"))
                         ),
                tabPanel("Individual", value = "individual",
                         plotOutput("individual_plot")),
                tabPanel("Grouped", value = "grouped",
                         plotOutput("grouped_plot"))
        
                    )
    )
)
)

# Define server logic required to draw a histogram
server <- function(input, output) {
    # Upload ---------------------------------------------------------------
    raw <- reactive({
        req(input$file)
        #delim <- if (input$delim == "") NULL else input$delim
        # we leave as NULL to guess
        delim <- NULL
        
        # col classes
        flow_classes <-  cols(
            datetime = col_datetime(),
            mac = col_character(),
            movement = col_double(),
            x = col_double(),
            y = col_double(),
        )
        
        li <- lapply(input$file$datapath,
                     function(tt)
                         vroom::vroom(tt, delim = delim, skip = 0,
                                      col_types = flow_classes)
        )
        names(li) <- input$file$datapath
        return(li)
    })
    
    # Get dates --------
    
    get_date_range <- reactive({
        out <- list(from = input$dateRange[1],
                    to = input$dateRange[2])
        out <- lapply(out, as.POSIXct)
        return(out)
    })
    
    # Clean ----------------------------------------------------------------
    tidied <- reactive({
        req(input$file)
        # get raw data
        li <- raw()
        # give them names
        names(li) <- get_fed_names()
        # code for a plot
        df <- bind_rows(li, .id = "file") 
        
        # filter dates 
        filter_dates <- get_date_range()
        df <- df %>%
            filter(between(date, filter_dates$from, filter_dates$to)) %>%
            mutate(date = lubridate::as_datetime(date))
        
        ## Add FR_Ratio (make compatible with FED2)
        if("FR_Ratio" %in% names(df) == FALSE){
            df <- df %>% mutate(FR_Ratio = 1)
        }
        return(df)
    })
    

}

# Run the application 
shinyApp(ui = ui, server = server)


