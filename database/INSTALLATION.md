### Installation guide

We provide a step by step installation guide to help installing the MongoDB client and locally running the RM database.
The installation guide relies on the use of the MongoDB Compass which should be downloaded from https://www.mongodb.com/try/download/compas .


## 1. Installing MongoDB server

To install the database locally the MongoDB server has to be installed which can be done on
the official MongoDB page (https://www.mongodb.com/try/download/community). After the download the installation processes can start where we
recommend using the option "Install MongoDB as a Service" once the choice comes up. This makes
an automatic start of the database in the background possible.

Verifying the successfull installation depends on the OS:

Linux and macOS: Type `mongod --version` into the console

Windows: Go into the settings for `services` and check for `MongoDB` in the list

The server adress to the database should be `mongodb://localhost27017` per default.

## 2. Starting the server

Linux: In most linux distributions the server can be started in the terminal by typing `sudo systemctl start mongod`
        and to check if the server is active type `sudo systemctl status mongod`.
        
macOS: The server can be started using Homebrew by typing `brew services start mongodb-community` into bash
        and to check if the server is active type `brew services list`.
        If you don't use Homebrew you can type `mongod –config /usr/local/etc/mongod.conf` into bash,
        but it is important to check where the files are located, since this may differ. The activity
        can be checked by typing `mongosh` into bash and a MongoDB shell should appear if it is running.
        
Windows: The server can be started by typing `net start MongoDB` into the PowerShell command line
        and to check if the server is active type `sc query MongoDB`.

## 3. Connecting the MongoDB Compass and add a new database

After opening the MongoDB Compass the connection to the database can be established by
adding the local server adress into the window which opens after pressing `add new connection`.

The new database can be added by pressing the according button in the interface. The name
you chose there will be referred to as the client. In the newly added database you can then
add collections which are the place the data has to be inserted to. To add the data into the
collection, simply open the created collection and press the green `+` and import the provided
.json file in `/data`

## 4. Using the database in python

The use of the database in python relies on the package `pymongo` which is available on
the usual installers. For each use, the python file (or notebook) has to establish a
connection with the database and the collection that has to be used. Our example uses
the name "quasar_db" for the database and "objects" for the collection with RM data.

  `from pymongo import MongoClient`
  
  `client = MongoClient("mongodb://localhost:27017")`
  
  `db = client["quasar_db"]`
  
  `objects = db["objects"]`

A routine to retrive all objects with a H$\beta$ lag measurement and a continuum luminosity at 5100\AA
and add their name and redshift to a list can look like this:

        names = []

        redshift = []

        results = objects.find({
        "properties.lags.H_beta": {"$exists": True},
        "properties.luminosities.L5100": {"$exists": True}
        })

        for quasar in results:

                entry_names = quasar.get("names")

                names.append(entry_names)

                entry_redshift = quasar.get("properties").get("redshift")

                redshift.append(entry_redshift["value"])
  
