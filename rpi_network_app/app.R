# This app has to run from the directory where the RPi network send the data 
# Originally this was /home/choilab/raspberry_IP/

library(shiny)
# we need dplyr 0.8.99.9 version or older..
library(tidyverse)
library(DT)
# devtools::install_github('wleepang/shiny-directory-input')
# this will only work if app is running on the local machine, will not work if app is deployed
# we are using shinyFiles instead
library(shinyFiles)

# helper function to scan pi directory
scan_pi_folder <- function(pi_folder){
    ip <- list.files(pi_folder, pattern="_ip.txt", full.names = TRUE)
    scan_running <- list.files(pi_folder, pattern = "running.txt", full.names=TRUE)
    if (is.character(scan_running) && length(scan_running) == 0) {
        # make empty data.frame
        running <- data.frame(datetime = "", stringsAsFactors = FALSE)
    } else {
        running <- read_tsv(scan_running, col_names = "datetime", col_types = cols(datetime = col_character()))
    }
    li <- list(read_tsv(ip, col_names =  FALSE),
               running)
    names(li) <- c(pi_folder, paste0(pi_folder, "_running"))
    return(li)
}

# helper function to check time deltas in minutes
is_online <- function(datetime, time_delta = 10){
    difference <- as.numeric(difftime(Sys.time(), datetime, units = "min"))
    flag <- difference < time_delta
    # change NA for FALSE
    #flag <- ifelse(is.na(flag), FALSE, flag)
    return(flag)
}


# helper to create inputs
shinyInput <- function(FUN, len, id, ...) {
    inputs <- character(len)
    for (i in seq_len(len)) {
        inputs[i] <- as.character(FUN(paste0(id, i), ...))
    }
    inputs
}

# helper to pool ips
pool_ip <- function(){
    # list files
    mac_address <- list.files(pattern="[a-z|0-9]{2}:")
    # now go get all ip values
    ip_list <- lapply(mac_address, scan_pi_folder)
    return(ip_list)    
}

# helper to process data
process_data <- function(ip_list){
    # To understand this command and see the previous lapply version
    # check https://stackoverflow.com/questions/60764653/tidier-reshape-for-list-of-data-frames-n-x-2-data-frames-to-single-data-frame
    df <- map_dfr(.x = ip_list,  ~ 
                      .x %>%
                      bind_cols %>%
                      mutate(datetime = lubridate::ymd_hms(datetime)), .id = 'grp')  %>% 
        # separate X1 into the value and the words
        separate(X1, into = c('grp1','val'), sep=":\\s*", extra = "merge") %>%
        # get the first word (MAC or IP), toss the rest
        mutate(grp1 = word(grp1, 1)) %>%
        # get the names_from grp1 column (which has MAC, IP for each machine) and values are in val
        pivot_wider(names_from = grp1, values_from = val) %>%
        # only keep the useful stuff and rename
        select(mac = MAC, ip = IP, datetime) 
    
    # now check whether stuff is online
    # and add buttons
    # the gist of how we are doing this is in this SO question
    # https://stackoverflow.com/questions/45739303/r-shiny-handle-action-buttons-in-data-table
    
    df <- df %>%
        mutate(
            # datetime comes in UTC, let's get it to local timezone
            datetime = lubridate::with_tz(datetime),
            last_update = as.numeric(difftime(Sys.time(), datetime, units = "min")),
            # convert to readable
            last_update = paste(round(last_update, 2), "min ago"),
            online = is_online(datetime),
            control = shinyInput(actionButton, nrow(df),
                                'button_', label = "Remote control",
                                onclick = 'Shiny.onInputChange(\"remote_control\",  this.id)' ),
            stream = shinyInput(actionButton, nrow(df),
                                'button_', label = "View",
                                onclick = 'Shiny.onInputChange(\"select_button\",  this.id)' )
        )
    return(df)
}


# Pool raspberry data -----------------------------------------------------
read_opt_flow <- function(file){
    # guess columns for back-ward compatibility
    fake <- read_csv(file, n_max = 10)
    
    if(ncol(fake) > 1){
        flow_df <- read_csv(file, col_names = c("datetime", "movement", "x", "y")) %>%
                    # replace first elment by zero
                    mutate(movement = replace(movement, 1, 0))
        # clean and transform to numeric
        flow_df <- flow_df %>% 
            mutate(x = as.numeric(str_extract(x, "[0-9]+")),
                   y = as.numeric(str_extract(y, "[0-9]+")))
    
    } else {
        flow_df <- read_csv(file, col_names = c("movement")) %>%
            # replace first elment by zero
            mutate(total_flow = replace(movement, 1, 0))
    }
    return(flow_df)
}

order_opt_flow <- function(date){
    # raspberries will send info to the mac/ folder
    # this function moves them from the mac/ to mac/date/opt_flow
    # we don't want to use list.files(recursive = TRUE) because we will get matches for all images
    # we get the dirs and then get the files only one level down
    dirs <- list.dirs(recursive=FALSE)
    pattern_to_find <- paste0(date,".*_opt_flow.csv")
    files_inside <- lapply(dirs, function(tt) list.files(tt, pattern = pattern_to_find, full.names=TRUE)) %>%
        unlist()
    file_df <- 
        tibble(
            full_files = files_inside,
            date =  str_extract(full_files, "[0-9]{4}-[0-9]{2}-[0-9]{2}"),
            base = basename(full_files),
            root_dir = dirname(full_files),
            new_dir = ifelse(str_detect(string = base, pattern = pattern_to_find), 
                             file.path(root_dir, date, "opt_flow"),
                             file.path(root_dir, date)),
            new_path = file.path(new_dir, base)
        )
    
    if (nrow(file_df)>0){
        # decreasing=FALSE helps the keep the order 
        # date/ followed by date/opt_flow 
        unique_dirs <- sort(unique(file_df$new_dir), decreasing=FALSE)
        print(unique_dirs)
        # create dirs
        lapply(unique_dirs, function(tt) if(dir.exists(tt) == FALSE) dir.create(tt, recursive = TRUE))
        # move files
        file.rename(file_df$full_files, file_df$new_path)
        return(file_df)
    } else {
        # return empty data frame
        return(data.frame())
    }
    
}

pool_movement_data <- function(date){
    # order files into the correct place
    # this will move files to proper folders
    ordered_files <- order_opt_flow(date)
    if (nrow(ordered_files) > 0){
        # get the list of files for that date from the new column and assign the names
        files <- ordered_files$new_path
        names(files) <- ordered_files$new_path
        # read each csv file and do cleaning
        pooled_data <- purrr::map(files,
                                  function(tt) read_opt_flow(tt)) %>%
            # pool all animals together
            bind_rows(.id="filename") #%>% 
                # clean
                # This adds a column that can be generated later for analysis purposes using the filename
                # I chose to comment it to reduce space on the final file
                # mutate(mac = str_extract(filename, "[a-z|0-9]{2}:.*/"),
                #       mac = str_remove(mac, "/"),
                #)
        return(pooled_data)
    } else {
        return(ordered_files)
        }
    } 

# helper to call raspberries from central computer
# this relies on sshpass and it's not the safest way to do it but it's probably fine

request_movement_data <- function(df, date){
    # Give some user feedback on UI
    showModal(modalDialog("Looking for data... Please wait.", easyClose = FALSE))
    for (machine in df$ip){
        print(paste("Trying to connect to", machine))
        python_command <- 'python3 /home/pi/homecage_quantification/send_movement_data.py -date'
        python_command <- paste(python_command, date)
     # create request call
       cmd_command <- paste0(" sshpass -p 'choilab' ssh -tt pi@", machine)
     # add python call to the sshpass
       cmd_command <- paste(cmd_command, python_command)
       system(cmd_command)
    }
    print("Done")
    removeModal()
    pooled_data <- pool_movement_data(date)
    return(pooled_data)
}


request_thermal_data <- function(df, date){
    # Give some user feedback on UI
    showModal(modalDialog("Looking for data... Please wait."))
    for (machine in df$ip){
        print(paste("Trying to connect to", machine))
        python_command <- 'python3 /home/pi/homecage_quantification/send_thermal_data.py -date'
        python_command <- paste(python_command, date)
        # create request call
        cmd_command <- paste0(" timeout 30s sshpass -p 'choilab' ssh -tt pi@", machine)
        # add python call to the sshpass
        cmd_command <- paste(cmd_command, python_command)
        print(cmd_command)
        system(cmd_command)
    }
    print("Done")
    removeModal()
    # order files into folders
    # mac/img/date
    # this will return either "files were moved"/"no files"
    result <- order_imgs()
    return(result)
}

# helper to order thermal images ----
order_imgs <- function(){
    # raspberries will send info to the mac/ folder
    # this function moves them from the mac/ to mac/date/img
    # we don't want to use list.files(recursive = TRUE) because we will get matches for all images
    # we get the dirs and then get the files only one level down
    dirs <- list.dirs(recursive=FALSE)
    files_inside <- lapply(dirs, function(tt) list.files(tt, pattern = "capture", full.names=TRUE)) %>%
        unlist()
    
    file_df <- 
    tibble(
    full_files = files_inside,
    date =  str_extract(full_files, "[0-9]{4}-[0-9]{2}-[0-9]{2}"),
    base = basename(full_files),
    root_dir = dirname(full_files),
    new_dir = ifelse(str_detect(string = base, pattern = ".jpg"), 
                     file.path(root_dir, date, "img"),
                     file.path(root_dir, date)),
    new_path = file.path(new_dir, base)
    )
    
    if (nrow(file_df)>0){
        # decreasing=FALSE helps the keep the order 
        # date/ followed by date/img 
        unique_dirs <- sort(unique(file_df$new_dir), decreasing=FALSE)
        print(unique_dirs)
        # create dirs
        lapply(unique_dirs, function(tt) if(dir.exists(tt) == FALSE) dir.create(tt, recursive=TRUE))
        # move files
        file.rename(file_df$full_files, file_df$new_path)
        return("files were moved")
    } else {
        return("no files")
    }
    
}




# UI side -----------------------------------------------------------------
# Define UI for application 

ui <- fluidPage(

    # Application title
    titlePanel("Raspberry Pi system"),
    
    # side panel ----
    # Sidebar with a slider input for number of bins 
    sidebarLayout(
        sidebarPanel(
            #directoryInput('directory', label = 'Select a directory or create one for a new experiment.'),
            h4("Experiment Folder"),
            tags$p("Select an existing directory or create a new one for a new experiment."),
            shinyDirButton("directory", "Folder select", "Select a directory or create one for a new experiment.",
                           icon = icon("folder")),
            tags$hr(),
            #tags$h4("The output of a folder selection"),
            tags$p(HTML("All data will go to the selected directory. You are currently working from this directory:")),
            verbatimTextOutput("directorypath"),
            tags$hr(),
            h4("Folder Contents"),
            p(HTML("Below you can see a list of the .csv files in the selected folder.")),
            htmlOutput(outputId = "file_list")
        ),

        # Show a plot of the generated distribution
        mainPanel(
            DT::dataTableOutput("ls"),
            hr(),
            h4(strong("Download current table")),
            fluidRow(
                column(width = 6,
                       downloadButton("download_csv",
                                      label = "Download csv",
                                      class = "btn-block")),
                column(width = 6,
                       downloadButton("download_pdf",
                                      label = "Download pdf",
                                      class = "btn-block"))
                ),
            hr(),
            fluidRow(
            h4(strong("Retrieve movement data")),
            column(width=3,
            dateInput("movement_date", value=Sys.Date(), label = "Select experiment date")),
            column(width = 4, style = "margin-top: 25px;", #margin-top needed for alignment
                   actionButton("retrieve_movement", "Get data"))
            ),
            hr(),
            fluidRow(
            h4(strong("Retrieve thermal data")),
            column(width=3,
                   dateInput("thermal_date", value=Sys.Date(), label = "Select experiment date")),
            column(width = 4, style = "margin-top: 25px;", #margin-top needed for alignment
                   actionButton("retrieve_thermal", "Get data"))
            )
        )
    )
)

# Server side -------------------------------------------------------------

# Define server logic required to draw a histogram
server <- function(input, output, session) {
    # experiment folder  ---
    # check the example to see how it works
    # shinyFiles::shinyFilesExample()
    volumes <- c(Home = fs::path_home(), "R Installation" = R.home(), getVolumes()())
    shinyDirChoose(input, "directory", roots = volumes,
                   session = session, restrictions = system.file(package = "base"))
    
    display_ls <- reactive({
        # if it doesn't exist, it will give logical(0) or FALSE
        # sum(...) will give TRUE only if exists
        if (sum(dir.exists(parseDirPath(volumes, input$directory)))) {
            listcsv <- list.files(parseDirPath(volumes, input$directory), pattern = ".csv")
            if(length(listcsv)> 0){
                output$file_list <- renderText(paste0("<p>", listcsv, "</p>"))
            } else {
                output$file_list <- renderText("No .csv files in this folder.")
            }
        } else {
            output$file_list <- renderText("<p>No directory has been selected yet </p>")
        }
    })
    
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
    # update retrieval      
    display_ls()
    
    })

    # We need to pool IPs once 
    ip_list <- pool_ip()
    df <- process_data(ip_list)
    # This updates the render, which help with the buttons on the table and info
    # all other df manipulations on the server side are done to the first df object
    observe({
        # let's use 5 mins = 300 sec = 300 * 10^3 ms
        invalidateLater(300 * 10^3, session)
        print("Refreshing IP info")
        # but we want to update this
        df <- process_data(ip_list)
        # df rendering ----
        output$ls <- DT::renderDataTable(
            # datetime gets shown in UTC, using formatdate messes with the buttons
            datatable(dplyr::select(df, -datetime), escape = FALSE, selection = 'none') %>% formatStyle(
                'online',
                target = 'row',
                backgroundColor = styleEqual(c(1), c('lightgreen'))
            )
        )
    })
    
    
    # IP stream video rendering in new tab ----
    observeEvent(input$select_button, {
        selectedRow <- as.numeric(strsplit(input$select_button, "_")[[1]][2])
        ip_target <- df[selectedRow, ] %>% pull("ip")
        # hardcoded port may crash
        port <- ":5000"
        # we need the http otherwise it doesn't work
        browseURL(paste0("http://", ip_target, port))
    })
    
    # VNC remote control ------
    observeEvent(input$remote_control, {
        selectedRow <- as.numeric(strsplit(input$remote_control, "_")[[1]][2])
        ip_target <- df[selectedRow, ] %>% pull("ip")
        # call vnc viewer
        cmd_call <- paste("vncviewer", ip_target)
        system(cmd_call)
    })
    
    # download data as table ----
    output$download_csv <- downloadHandler(
        filename = function() {
            paste0(lubridate::today(), "_ip_data.csv")
        },
        content = function(file) {
            vroom::vroom_write(dplyr::select(df, mac, ip, last_update), file)
        }
    )
    
    output$download_pdf <- downloadHandler(
        filename = function(){paste0(lubridate::today(), "_ip_data.pdf")},
        content = function(file) {
            pdf(file, height=11, width=8.5)
            gridExtra::grid.table(dplyr::select(df, mac, ip, last_update) %>% 
                                      rename(`Last update` = last_update),
                                  # make font big
                                  theme = gridExtra::ttheme_default(base_size = 18,
                                                                    core = list(padding=unit(c(10, 6), "mm")))
                                  )
            dev.off()    
        }
    )
    
    # request movement data observer ---
    observeEvent(input$retrieve_movement, {
        # before searching, check that you have a place to save the files
        if (is.integer(input$directory)) {
            showModal(modalDialog("Please select the directory where you want to save the files and try again",
                                  easyClose = FALSE,
                                  title = "Directory not specified"))
        } else {
            # This will request the data and create a dataframe object
            # with all data for that date, all machines together
            pooled_data <- request_movement_data(df, date=input$movement_date)
            if(nrow(pooled_data) == 0){
                showNotification("Looks like there's no data. Check date.", type = "error")
            } else {
                showNotification("Data retrieved :)", type = "message")
                head(pooled_data)
                # Write pooled data into directory as compressed .csv.gz
                readr::write_csv(pooled_data,
                                 file.path(
                                     parseDirPath(volumes, input$directory),
                                     paste0(input$movement_date, "_pooled_movement_data.csv.gz"))
                )
                # once we wrote, display the file list  
                display_ls()
                
            }
            
        }
    })
    # request thermal data observer ---
    observeEvent(input$retrieve_thermal, {
        # This will request the data and create a dataframe object
        # with all data for that date, all machines together
        result <- request_thermal_data(df, date=input$thermal_date)
        if(result == "no files"){
            showNotification("Looks like there's no data. Check date.", type = "error")
        } else {
            showNotification("Data retrieved :)", type = "message")    
        }
    })
    

}

# Run the application ------- 
shinyApp(ui = ui, server = server)
