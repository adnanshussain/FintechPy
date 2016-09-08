from webapp import theapp, active_config

###############################
### Run the App             ###
###############################
if __name__ == "__main__":
    theapp.run(host=active_config.HOST, port=active_config.PORT)