from webapp import theapp, config

###############################
### Run the App             ###
###############################
if __name__ == "__main__":
    theapp.run(host=config.DevConfig.HOST, port=config.DevConfig.PORT)