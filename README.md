# umpire
This project seeks to compete in the the [Ghana-ai-hackathon-25](https://github.com/Bridge-Labs-Tech/ghana-ai-hackathon-25)




## 🔧 Database Setup

To create the PostgreSQL database and user required for this project, follow the steps below:

### 1. 📄 Create a `.env` file in the project root

This file should contain your PostgreSQL user credentials:

```env
UMPIRE_TYPE_STORAGE
UMPIRE_DB_USER
UMPIRE_DB_PWD
UMPIRE_DB
UMPIRE_DB_HOST
UMPIRE_DB_PORT
```

Make sure the following SQL files exist in the data/ directory:
- create_db.sql: Contains the CREATE DATABASE command.
- create_tables.sql  Contains the CREATE TABLE commands.

Depending on your platform:

On Linux / WSL:
```
chmod +x create_postgres_db.sh
./create_postgres_db.sh
```
On Windows PowerShell:
```
.\create_postgres_db.ps1
```

To populate data into into the umpire_db, run:  
```
python data/modeling/populate_db.py
```
14 different tables are created

![plot](./assets/schema.png)


## Prediction endpoints

1. Route Demand predictions:

2. Travel Time Predictions:

## 🔧Start the flask app

```
python -m backend.dev_flask.app  
```



## Authors
Below are the contributors to the project:

- [Andrew](https://github.com/kojomensahonums)
- [Adobea](https://github.com/adobea-dev)
- [William](https://github.com/williamgrey1)
- [Samuel Amihere](https://github.com/SamuelAmihere)