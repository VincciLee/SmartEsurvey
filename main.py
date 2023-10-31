# Programmer Name: Ms Lee Wen Xi, APD3F2211CS(IS)
# Program Name: main.py
# Description: A script to startup the system
# First Written On: 01/06/2023
# Last Edited On:  22/07/2023

from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
