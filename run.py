from webapp import app, config

###############################
### Run the App             ###
###############################
if __name__ == "__main__":
    app.theapp.run(host=config.DevConfig.HOST, port=config.DevConfig.PORT)