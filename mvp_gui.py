import tkinter as tk
from tkinter import filedialog
import requests
import base64
import json
import datetime
from calendar import monthrange
import pymongo
import mongoengine
from mongoengine import StringField, ListField, DateTimeField, DictField
import pandas as pd
from bson import json_util, ObjectId
from gridfs import GridFS, GridFSBucket
import csv
from tkinter import messagebox
from tkinter import simpledialog
import tkinter as tk
from tkinter import filedialog, simpledialog
from tkinter import simpledialog as sd

# Convert the json called from the database into an excel
def get_excel(database_name, collection_name):
    # Credentials
    user = "dmarroquin"
    passw = "tN9XpCCQM2MtYDme"
    host = "nucmonitordata.xxcwx9k.mongodb.net"

    # Connect to the MongoDB database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passw}@{host}/?retryWrites=true&w=majority"
    )
    db = client[database_name]
    collection = db[collection_name]

    # Retrieve the latest document from the collection
    # latest_doc = collection.find_one({}, {"_id": 0}, sort=[("_timestamp", pymongo.ASCENDING)])
    latest_doc = collection.find().sort({"_id": -1}).limit(1)

    if latest_doc:
        # Convert the data to a DataFrame
        data_df = pd.DataFrame(latest_doc)
        if collection_name == "filtered":
            # Specify the path and filename for the Excel file
            excel_file_path = "filtered_unavailabilities.xlsx"
        elif collection_name == "photo_date":
            excel_file_path = "photo_date.xlsx"

        # Export the DataFrame to Excel with index
        data_df.to_excel(excel_file_path, index=True)

    # Close the database connection
    client.close()

def get_excel_local(data, path, photo_date):
    data_df = pd.DataFrame(data)
    if photo_date:
        excel_file_path = "photo_date.xlsx"
    else:
        excel_file_path = "filtered_unavailabilities.xlsx"
    # Export the DataFrame to Excel with index
    data_df.to_excel(path + excel_file_path, index=True)

# --------------------------------------------------------------------------------------- #

# Access the raw files without storing locally
def access_files_from_mongodb(database_name, collection_name):
    # Credentials
    user = "dmarroquin"
    passw = "tN9XpCCQM2MtYDme"
    host = "nucmonitordata.xxcwx9k.mongodb.net"

    # Connect to the MongoDB database
    client = pymongo.MongoClient(
        "mongodb+srv://{0}:{1}@{2}/?retryWrites=true&w=majority&connectTimeoutMS=5000"
        .format(user, passw, host))

    db = client[database_name]
    fs = GridFSBucket(db, collection_name)

    # List all the files in the collection
    files = db[collection_name + '.files'].find()

    # Access the files
    for file in files:
        file_id = file['_id']
        file_name = file['filename']

        # Open the file
        with fs.open_download_stream(file_id) as file_stream:
            # Read the file contents
            file_contents = file_stream.read()
            
            # Convert file contents to JSON
            json_data = json.loads(file_contents)

            # Example: Print the processed data
            json_data

    # Close the database connection
    client.close()
    return json_data

# --------------------------------------------------------------------------------------- #

# Store data with more than 16MB in a collection using GridFS
def mongo_store_large_data(json_data, database_name, collection_name):
    # Credentials
    user = "dmarroquin"
    passw = "tN9XpCCQM2MtYDme"
    host = "nucmonitordata.xxcwx9k.mongodb.net"

    # Connect to the MongoDB database
    client = pymongo.MongoClient(
        "mongodb+srv://{0}:{1}@{2}/?retryWrites=true&w=majority&connectTimeoutMS=5000"
        .format(user, passw, host))
    db = client[database_name]
    fs = GridFS(db, collection_name)

    # Convert JSON data to string
    json_string = json.dumps(json_data)

    # Store the JSON data in GridFS as a single file
    file_id = fs.put(json_string.encode(), filename='data.json')

    # Close the database connection
    client.close()

    return file_id

# --------------------------------------------------------------------------------------- #

# Store normal size data
def mongo_store_data(data, database_name, collection_name):
    # Credentials
    user = "dmarroquin"
    passw = "tN9XpCCQM2MtYDme"
    host = "nucmonitordata.xxcwx9k.mongodb.net"

    # Connect to the MongoDB database
    client =  pymongo.MongoClient(
    "mongodb+srv://{0}:{1}@{2}/?retryWrites=true&w=majority&connectTimeoutMS=5000" \
    .format(user, passw, host))

    db = client[database_name]
    collection = db[collection_name]

    # Insert the data into the collection
    collection.insert_one(data)

    # Close the database connection
    client.close()

# --------------------------------------------------------------------------------------- #

# Convert the dictionary of dictionaries to JSON
def convert_to_json(item):
    if isinstance(item, dict):
        return {str(k): convert_to_json(v) for k, v in item.items()}
    elif isinstance(item, list):
        return [convert_to_json(i) for i in item]
    elif isinstance(item, ObjectId):
        return str(item)
    else:
        return item
# --------------------------------------------------------------------------------------- #

# The idea of this function is to sum the total availability for each day of interest
# This is already done in the Excel so it might be useful to check
# Function gives the total of the data. When printed as dataframe/excel,
# Will give a final row with the total for each plant and the total overall
def add_total(data):
    total_values = {}
    for key in data:
        daily_values = data[key]
        total = sum(daily_values.values())
        daily_values["Total"] = total
        for date, value in daily_values.items():
            if date not in total_values:
                total_values[date] = value
            else:
                total_values[date] += value
        
    data["Total"] = total_values

# --------------------------------------------------------------------------------------- #

# Function to create an authentication token. This token is then used in the HTTP requests to the API for authentication.
# It is necessary to receive data from RTE.
def get_oauth():
    # ID from the user. This is encoded to base64 and sent in an HTTP request to receive the oauth token.
    # This ID is from my account (RMP). However, another account can be created in the RTE API portal and get another ID.
    joined_ID = '057e2984-edb3-4706-984b-9ea0176e74db:dc9df9f7-9f91-4c7a-910c-15c4832fb7bc'
    b64_ID = base64.b64encode(joined_ID.encode('utf-8'))
    b64_ID_decoded = b64_ID.decode('utf-8')
    
    # Headers for the HTTP request
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Authorization': f'Basic {b64_ID_decoded}'}
    api_url = 'https://digital.iservices.rte-france.com/token/oauth/'
    # Call to the API and if successful, the response will be 200.
    response = requests.post(api_url, headers=headers)
    
    # When positive response, the token is retrieved
    data = response.json()
    oauth = data['access_token']
    
    return(oauth)

# --------------------------------------------------------------------------------------- #

# This function does severall calls to the RTE API (because maximum time between start_date and end_date is 1 month) 
# the argument past_photo is a boolean (True, False) that indicates if we want to make a photo from the past or not
# However, the past_photo part and past_date is not yet implemented.
def get_unavailabilities(path_to_store, oauth, years, months, past_photo, past_date=None):
    # This should be changed in the case of getting a past_photo because many of the rows that are relevant for that 
    # past photo will not be ACTIVE anymore.
    # unav_status = ['ACTIVE', 'INACTIVE']
    # This could also be changed. Currently it means that if we call the API with start_date=01/01/2023 and end_date=01/02/2023,
    # it will return all the records of unavailabilities that have been updated between the two dates.
    # date_type = 'UPDATED_DATE'
    # date_type APPLICATION_DATE gets all unavailabilities with predictions in the defined dates, so that 
    # we can get an unavailability that has updated_date outside the defined dates for start_date and end_date
    date_type = 'APPLICATION_DATE'
    
    # Current year/month/day/hour/minute/second is calculated for the last call to the API. For instance, if today is 05/05/2023,
    # the last call of the API will be from 01/05/2023 to 05/05/2023 (+current hour,minute,second). 
    current_datetime = datetime.datetime.now()
    current_year = current_datetime.strftime('%Y')
    current_month = current_datetime.strftime('%m')
    current_day = current_datetime.strftime('%d')
    current_hour = current_datetime.strftime('%H')
    current_minute = current_datetime.strftime('%M')
    current_second = current_datetime.strftime('%S')
    
    # Headers for the HTTP request
    headers = {'Host': 'digital.iservices.rte-france.com',
               'Authorization': f'Bearer {oauth}'
        }
    
    # the responses object is where we are going to store all the responses from the API.
    # Initially, current_datetime is included to know when we have called the API and all the
    # individual results of the API (because each call is Maz 1 month) are stored in responses["results"]
    responses = {"current_datetime": current_datetime.strftime("%m/%d/%Y, %H:%M:%S"),
                 "results":[]
        }
    
    # Loop to call the API all the necessary times.
    for i in range(len(years)):
        for j in range(len(months)): 
            
            # start_year and start_month of current call to the API
            start_year = years[i]
            start_month = months[j]
            # start_date is constructed. Now we only need to construct end_date, for which there are 2 options.
            start_date = f'{start_year}-{start_month}-01T00:00:00%2B02:00'
            
            # This if statement checks that the year and month of study are earlier or equal to the current month and year.
            # This is because when calling the API with date_type='UPDATED_DATE', future dates are not valid.
            if int(start_year) <= int(current_year):
                # Case 1: Current month and current year --> end_date will be the current date.
                if start_year == current_year:
                    end_date = f'{current_year}-{current_month}-{current_day}T{current_hour}:{current_minute}:{current_second}%2B02:00'
                    # print(f'We are in the current month and year, so the end date is {end_date}')
                # Case 2: Different month or year from current date
                else:
                 # Calculate the number of days in the current month
                    _, num_days = monthrange(int(start_year), int(start_month))
                    end_date = f'{start_year}-{start_month}-{num_days}T23:59:59%2B02:00'
                    
                print(f'start date is {start_date}')
                print(f'end date is {end_date}')
                
                # Call to the API
                # api_url = f'https://digital.iservices.rte-france.com/open_api/unavailability_additional_information/v4/generation_unavailabilities?status={unav_status}&date_type={date_type}&start_date={start_date}&end_date={end_date}'
                api_url = f'https://digital.iservices.rte-france.com/open_api/unavailability_additional_information/v4/generation_unavailabilities?date_type={date_type}&start_date={start_date}&end_date={end_date}'

                response = requests.get(api_url, headers=headers)
                json_response = response.json()
                responses["results"].append(json_response)

    
    # Store the responses in MongoDB
    database_name = "data"
    collection_name = "raw"
    # raw_file = '/Users/diegomarroquin/HayaEnergy/data/unavailabilities_07-06.json'
    mongo_store_large_data(responses, database_name, collection_name)
    # mongo_append_large_data(responses, database_name, collection_name)
    # mongo_store_data(responses, database_name, collection_name)

    # mongo_append_data(responses, database_name, collection_name)

    print("Data stored in database")
    # path to store the results locally
    file_path = path_to_store + f'/2_mass_unavailabilities_test.json'

    with open(file_path, "w") as write_file:
        # Serialize responses using json_util
        serialized_responses = json_util.dumps(responses)
        write_file.write(serialized_responses)

    print("Data stored locally")
    
    # user_input_excel = input("Would you like to get an excel of the RTE?: ")
    # if 'y' in user_input_excel.lower():
    #     get_excel(database_name, collection_name)
    #     print("Excel downloaded")
    #     return
        
# --------------------------------------------------------------------------------------- #

# this function does the proper analysis of the data
# It takes the user, password, host, to connect to the mongodb database and get
# the data to clean from the database from database and collection
# Create a condition that makes it so it only takes the ACTIVE when nucmonitor, and 
# all (INACTIVE, ACTIVE) when photo_date
def nuc_monitor(user, passw, host, database, collection, start_date, end_date, path_to_store):
    # # Slightly changed metadata to fit the data from the RTE API: ST-LAURENT B 2 --> ST LAURENT 2, ....

    # --------------------------------------------- #
    photo_date = False

    # file_path = "/Users/diegomarroquin/HayaEnergy/data/plants_metadata.json"

    # with open(file_path, "r") as file:
    #     plants_metadata = json.load(file)
    plants_metadata = {"BELLEVILLE 1": 1310.0, "BELLEVILLE 2": 1310.0, "BLAYAIS 1": 910.0, "BLAYAIS 2": 910.0, 
                   "BLAYAIS 3": 910.0, "BLAYAIS 4": 910.0, "BUGEY 2": 910.0, "BUGEY 3": 910.0, "BUGEY 4": 880.0, 
                   "BUGEY 5": 880.0, "CATTENOM 1": 1300.0, "CATTENOM 2": 1300.0, "CATTENOM 3": 1300.0, 
                   "CATTENOM 4": 1300.0, "CHINON 1": 905.0, "CHINON 2": 905.0, "CHINON 3": 905.0, 
                   "CHINON 4": 905.0, "CHOOZ 1": 1500.0, "CHOOZ 2": 1500.0, "CIVAUX 1": 1495.0, 
                   "CIVAUX 2": 1495.0, "CRUAS 1": 915.0, "CRUAS 2": 915.0, "CRUAS 3": 915.0, "CRUAS 4": 915.0, 
                   "DAMPIERRE 1": 890.0, "DAMPIERRE 2": 890.0, "DAMPIERRE 3": 890.0, "DAMPIERRE 4": 890.0, 
                   "FLAMANVILLE 1": 1330.0, "FLAMANVILLE 2": 1330.0, "GOLFECH 1": 1310.0, "GOLFECH 2": 1310.0, 
                   "GRAVELINES 1": 910.0, "GRAVELINES 2": 910.0, "GRAVELINES 3": 910.0, "GRAVELINES 4": 910.0, 
                   "GRAVELINES 5": 910.0, "GRAVELINES 6": 910.0, "NOGENT 1": 1310.0, "NOGENT 2": 1310.0, 
                   "PALUEL 1": 1330.0, "PALUEL 2": 1330.0, "PALUEL 3": 1330.0, "PALUEL 4": 1330.0, "PENLY 1": 1330.0, 
                   "PENLY 2": 1330.0, "ST ALBAN 1": 1335.0, "ST ALBAN 2": 1335.0, "ST LAURENT 1": 915.0, 
                   "ST LAURENT 2": 915.0, "TRICASTIN 1": 915.0, "TRICASTIN 2": 915.0, "TRICASTIN 3": 915.0, 
                   "TRICASTIN 4": 915.0, "FESSENHEIM 1": 880.0, "FESSENHEIM 2": 880.0}


    unav_API = access_files_from_mongodb(database, collection)

    # Store the unavailabilities in a list
    unavailabilities = []
    print("Unav")
    for unavailabilities_API in unav_API['results']:
        try:
            unavailabilities += unavailabilities_API['generation_unavailabilities']
        except:
            print('There was an error')
            # print(unavailabilities_API)
    print("Past unav")

# --------------------------- HERE IS THE CHANGE TO GET ONLY ACTIVE OR ACTIVE AND INACTIVE --------------------------- #

    photo_date = False
    photo_date_input = messagebox.askquestion("Photo Date", "Would you like the photo date?")
    if photo_date_input == "yes":
        past_date = simpledialog.askstring("Past Date", "Enter the cutoff date (yyyy-mm-dd): ")
        # past_date = datetime.datetime.strptime(past_date_dialog, "%Y-%m-%d").date()
        nuclear_unav = [d for d in unavailabilities if d['production_type'] == 'NUCLEAR' and d['updated_date'] <= past_date]
        photo_date = True
    else:
        nuclear_unav = [d for d in unavailabilities if d['production_type'] == 'NUCLEAR' and d['status'] == 'ACTIVE']
    # return print(past_date)
    

# --------------------------- HERE IS THE CHANGE TO GET ONLY ACTIVE OR ACTIVE AND INACTIVE --------------------------- #


    # The idea is to create a dictionary where the key is the ID of the unavailability and the value
    # is the number of the latest unavailability
    # TODO: If I am only asking for ACTIVE records from the API, I am only receinving the latest
    # version of each unavailability. On the contrary, if I am doing a past photo, this piece
    # of code is useful to get the latest version.
    
    identifiers_dict = {}
    for unav in nuclear_unav:
        identifier = unav['identifier']
        version = unav['version']
        
        if identifier in identifiers_dict:
            if identifiers_dict[identifier] < version:
                identifiers_dict[identifier] = version
        else:
            identifiers_dict[identifier] = version
            
    
    # Filter the unavailabilities to only include those with the latest version
    # Useful for the past photo case.
    filtered_unavs = [x for x in nuclear_unav if x['version'] == identifiers_dict[x['identifier']]]


    # The unavailabilities are ordered in a more simple way. This is done by creating a dictionary 
    # called results where each key is a name of a nuclear plant. Then the value of each key is a list
    # with the unavailabilities corresponding to that nuclear plant.
    results = {}

    for unav in filtered_unavs:
        plant_name = unav['unit']['name']
        if plant_name in results:
            # If the key is already in the dictionary, append unavailability to the list
            results[plant_name].append({'status': unav['status'],
                                        'identifier': unav['identifier'],
                                        'creation_date': unav['creation_date'],
                                        'updated_date': unav['updated_date'], 
                                        'start_date': unav['start_date'], 
                                        'end_date': unav['end_date'], 
                                        'available_capacity': unav['values'][0]['available_capacity']})
        else:
            # if the key of the plant is not there yet, create a new element of the dictionary
            results[plant_name] = [{'status': unav['status'],
                                    'identifier': unav['identifier'],
                                    'creation_date': unav['creation_date'],
                                    'updated_date': unav['updated_date'], 
                                    'start_date': unav['start_date'], 
                                    'end_date': unav['end_date'], 
                                    'available_capacity': unav['values'][0]['available_capacity']}]


    # Create a list with all the dates that are interesting to check. This is done by defining a start_date and an
    # end_date and getting all the dates in between
    # For each date of interest, the results will show all the predicted availability of each nuclear plant.
    dates_of_interest = [start_date]
    date_plus_one = start_date
    
    while date_plus_one < end_date:
        date_plus_one = date_plus_one + datetime.timedelta(days=1)
        dates_of_interest.append(date_plus_one)
        

    results_plants = {}
    # results = active_data
    # Each plant has a list of all the days of interest. For each day, the power of that day is also included. 
    # First step: put all the powers to the max power
    for plant_name, power in plants_metadata.items(): 
        pairs_date_power = [(date, power) for date in dates_of_interest]
        # Create a dictionary where days are keys and powers are values
        results_plants[plant_name] = dict(pairs_date_power)
    


    # Second step: for those days where the unavailability of a plant indeed decreases, this is updated in the dictionary 
    # results_plants
    for plant, unavailabilities in results.items():
        # original_power is the normal power of the plant
        original_power = plants_metadata[plant]
        # TODO: Check when there are two unavailabilities for the same day for the same plant. This would give problems.

        # Get all the unavailabilities scheduled for the plant.
        results_current_plant = results_plants[plant] 
        
        for unavailability in unavailabilities:
            # For each unavailability, the resulting power, start and end datetime are collected.
            power_unavailability = unavailability["available_capacity"]
            # The date comes as a string
            start_datetime_unav = unavailability["start_date"].split("+")[0].replace("T"," ").replace("-", "/")
            # string to datetime conversion. 
            # TODO: Maybe all the replacing that is done to the strings is not necessary? Not sure
            start_datetime_unav = datetime.datetime.strptime(start_datetime_unav, "%Y/%m/%d %H:%M:%S") #, '%m/%d/%y %H:%M:%S')
            end_datetime_unav = unavailability["end_date"].split("+")[0].replace("T"," ").replace("-", "/")
            end_datetime_unav = datetime.datetime.strptime(end_datetime_unav, "%Y/%m/%d %H:%M:%S")
            start_date_unav = start_datetime_unav.date()
            end_date_unav = end_datetime_unav.date()
            
            # For the current unavailability, we want to find which days it affects
            for day in dates_of_interest:
                if start_date_unav <= day and day <= end_date_unav:
                    # Four cases: 
                    #     1) start date smaller than day and end date bigger than day
                    #     2) start date equal to day and end date bigger than day
                    #     3) start date smaller than day and end date equal to day
                    #     4) start date equal to day and end date equal to day
                    
                    # Calculate the % of the day that the plant is under maintenance
                    percentage_of_day = None
                    # Case 1
                    if start_date_unav < day and day < end_date_unav:
                        percentage_of_day = 1
                    else:
                        start_hour = start_datetime_unav.hour
                        start_minute = start_datetime_unav.minute
                        end_hour = end_datetime_unav.hour
                        end_minute = end_datetime_unav.minute
                        # Case 2
                        if start_date_unav == day and day < end_date_unav:  
                            # percentage_of_day = 1 - (24*60 - (start_hour*60 + start_minute))/(24*60)
                            percentage_of_day = (24*60 - (start_hour*60 + start_minute))/(24*60)
                        # Case 3
                        elif start_date_unav < day and day == end_date_unav:
                            percentage_of_day = (end_hour*60 + end_minute)/(24*60)
                        # Case 4
                        elif start_date_unav == day and day == end_date_unav:
                            percentage_of_day = ((end_hour*60 + end_minute) - (start_hour*60 + start_minute))/(24*60)
                       
                    # The average power of the day is calculated
                    power_of_day = percentage_of_day*power_unavailability + (1-percentage_of_day)*original_power
                    # previous_result = results_current_plant[day]
                    results_current_plant[day] = power_of_day
                    # if previous_result != power_of_day:
                    #     print(f"Previous result was {previous_result} and the new one is {power_of_day}")

    add_total(results_plants)
    print("Done")
    print(results_plants)
    # Convert datetime key to string to store in mongodb
    results_plants = {plant: {str(date): power for date, power in plant_data.items()} for plant, plant_data in results_plants.items()}
    # -------------------------------------------------
    if photo_date == False:
        # Store the results_plants in MongoDB
        database_name = "data"  # Specify your database name
        collection_name = "filtered"  # Specify your collection name
        mongo_store_data(results_plants, database_name, collection_name)
        # print("Data stored in database")
        messagebox.showinfo("Success", "Nucmonitor results stored in database.")
        # mongo_replace_data(results_plants_total, database_name, "filtered_excel")
        # print("Data stored in database")
        # mongo_append_data(results_plants, database_name, collection_name)
        current_datetime = datetime.datetime.now()
        current_year = current_datetime.strftime('%Y')
        current_month = current_datetime.strftime('%m')
        current_day = current_datetime.strftime('%d')
        current_hour = current_datetime.strftime('%H')
        current_minute = current_datetime.strftime('%M')
        current_second = current_datetime.strftime('%S')

        json_file_path = path_to_store + f'/filtered_unavailabilities_test.json'  
        
        json_data = json.dumps(convert_to_json(results_plants))

        with open(json_file_path, "w") as results_file:
            json.dump(json_data, results_file)

        print("File stored in ", json_file_path)
        user_input_excel = messagebox.askquestion("Excel", "Would you like to get an excel of the NucMonitor?")
        if user_input_excel == "yes":
            # get_excel(database_name, 'filtered')
            get_excel_local(results_plants, path_to_store, photo_date)
            # messagebox.showinfo("Success", "Excel downloaded.")
            messagebox.showinfo("Success", "Excel stored in" + path_to_store)
        return
    else:
        database_name = "data"  # Specify your database name
        collection_name = "photo_date"  # Specify your collection name
        mongo_store_data(results_plants, database_name, collection_name)
        messagebox.showinfo("Success", "Photo Date results stored in database.")
        current_datetime = datetime.datetime.now()
        current_year = current_datetime.strftime('%Y')
        current_month = current_datetime.strftime('%m')
        current_day = current_datetime.strftime('%d')
        current_hour = current_datetime.strftime('%H')
        current_minute = current_datetime.strftime('%M')
        current_second = current_datetime.strftime('%S')

        json_file_path = path_to_store + f'/photo_date.json'  
        json_data = json.dumps(convert_to_json(results_plants))

        with open(json_file_path, "w") as results_file:
            json.dump(json_data, results_file)

        print("File stored in ", json_file_path)

        user_input_excel = messagebox.askquestion("Excel", "Would you like to get an excel of the Photo Date?")
        if user_input_excel == "yes":
            # get_excel(database_name, 'photo_date')
            get_excel_local(results_plants, path_to_store, photo_date)
            messagebox.showinfo("Success", "Excel stored in" + path_to_store)
        return
    # -------------------------------------------------
    return

def create_gui():
    def browse_directory():
        directory = filedialog.askdirectory()
        directory_entry.delete(0, tk.END)
        directory_entry.insert(tk.END, directory)

    def submit_form():
        database_name = database_entry.get()
        collection_name = collection_entry.get()
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        path_to_store = directory_entry.get()

        try:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please enter dates in YYYY-MM-DD format.")
            return

        nuc_monitor("dmarroquin", "tN9XpCCQM2MtYDme", "nucmonitordata.xxcwx9k.mongodb.net",
                    database_name, collection_name, start_date, end_date, path_to_store)
        messagebox.showinfo("Success", "NucMonitor results generated successfully.")

    # Create the GUI window
    window = tk.Tk()
    window.title("NucMonitor GUI")

    # Create and arrange the form elements
    tk.Label(window, text="Database Name:").grid(row=0, column=0, sticky=tk.E)
    tk.Label(window, text="Collection Name:").grid(row=1, column=0, sticky=tk.E)
    tk.Label(window, text="Start Date (yyyy-mm-dd):").grid(row=2, column=0, sticky=tk.E)
    tk.Label(window, text="End Date (yyyy-mm-dd):").grid(row=3, column=0, sticky=tk.E)
    tk.Label(window, text="Output Directory:").grid(row=4, column=0, sticky=tk.E)

    database_entry = tk.Entry(window)
    collection_entry = tk.Entry(window)
    start_date_entry = tk.Entry(window)
    end_date_entry = tk.Entry(window)
    directory_entry = tk.Entry(window)

    database_entry.grid(row=0, column=1)
    collection_entry.grid(row=1, column=1)
    start_date_entry.grid(row=2, column=1)
    end_date_entry.grid(row=3, column=1)
    directory_entry.grid(row=4, column=1)

    browse_button = tk.Button(window, text="Browse", command=browse_directory)
    browse_button.grid(row=4, column=2)

    submit_button = tk.Button(window, text="Submit", command=submit_form)
    submit_button.grid(row=5, column=1)

    # Start the GUI event loop
    window.mainloop()


if __name__ == "__main__":
    create_gui()
