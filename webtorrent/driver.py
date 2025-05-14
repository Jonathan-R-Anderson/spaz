from shared import (logging, app)




if __name__ == '__main__':
    logging.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=5002, debug=True, ssl_context=('/certs/fullchain.pem', '/certs/privkey.pem'))
