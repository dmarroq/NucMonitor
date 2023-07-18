# NucMonitor

The NucMonitor program is a Python script that interacts with the RTE (Réseau de Transport d'Électricité) API to retrieve and analyze data on nuclear power plant unavailabilities. It uses the tkinter library for creating a graphical user interface (GUI) to input the necessary parameters.

Future:
- API to connect to database
- Processes put into classes
- Frontend to view data


## Dependencies
The program requires the following dependencies:

tkinter: Used for creating the GUI.

requests: Used for making HTTP requests to the RTE API.

base64: Used for encoding and decoding data in Base64 format.

json: Used for working with JSON data.

datetime: Used for handling dates and times.

calendar: Used for getting the number of days in a month.

pymongo: Used for interacting with MongoDB.

mongoengine: Used for object-document mapping with MongoDB.

pandas: Used for working with tabular data.

bson: Used for working with BSON data.

gridfs: Used for storing and retrieving large files in MongoDB.

csv: Used for working with CSV files.

messagebox and simpledialog from tkinter: Used for displaying message boxes and dialog boxes in the GUI.

## Usage
To use the NucMonitor program, follow these steps:

Install the required dependencies mentioned above.
Import the necessary libraries in your Python script or interactive environment.
Copy and paste the entire program code into your script or save it as a separate Python file.
Ensure that the dependencies are properly installed and accessible in your environment.
Call the create_gui() function to start the GUI and enter the required parameters.
Enter the database name, collection name, start date, end date, and output directory in the GUI.
Click the "Browse" button to select the output directory.
Click the "Submit" button to start the NucMonitor analysis.
The program will retrieve data from the RTE API, process it, store it in a MongoDB database, and generate an Excel file (optional).
The results will be displayed in the GUI, and a message box will indicate the success of the operation.
Note: Ensure that you have the necessary credentials and permissions to access the RTE API and MongoDB database.

## Functionality
The NucMonitor program performs the following tasks:

Retrieves an authentication token from the RTE API using the get_oauth() function.
Retrieves unavailability data from the RTE API using the get_unavailabilities() function. The data is stored in a MongoDB database and saved locally in a JSON file.
Processes the retrieved unavailability data to calculate the power availability for each nuclear power plant and each day of interest.
Stores the processed data in a MongoDB database and saves it locally in a JSON file.
Generates an Excel file with the processed data (optional).
Displays the processed data in the GUI and provides the option to download the Excel file.

## Additional Notes
The program uses the tkinter library to create a graphical user interface. This allows users to input the necessary parameters and interact with the program more easily.
The program interacts with the RTE API to retrieve unavailability data. It requires authentication credentials and an access token to make the API calls.
The program uses MongoDB to store and retrieve data. It requires a MongoDB database connection and proper configuration.
The program provides options to store the raw unavailability data, as well as the processed data, in the MongoDB database.
The program can generate an Excel file containing the processed data for further analysis and reporting.
The program includes error handling and validation to ensure that the input parameters are in the correct format.
The program provides success message boxes to indicate the successful completion of each step.

