# umpire
This project seeks to compete in the the [Ghana-ai-hackathon-25](https://github.com/Bridge-Labs-Tech/ghana-ai-hackathon-25)




## 🔧 Database Setup

To create the PostgreSQL database and user required for this project, follow the steps below:

### 1. 📄 Create a `.env` file in the project root

This file should contain your PostgreSQL superuser credentials:

```env
PGUSER=<postgres>
PGPASSWORD=<your_password>
PGHOST=localhost
PGPORT=5432
```

Make sure the following SQL files exist in the data/ directory:
- create_db.sql: Contains the CREATE DATABASE command.

Depending on your platform:

On Linux / WSL:
```
$ chmod +x create_postgres_db.sh
$ ./create_postgres_db.sh
```
On Windows PowerShell:
```
> .\create_postgres_db.ps1
```
## Assigned Tasks

1. ML:
    - Travel time on a route: Andrew, Adobea
    - Daily Demands on a route: Andrew, Adobea
    - Number of stops on a route: Williams, Samuel

2. Vehicle Assignment on to routes
    - Vehicle Assignment: Samuel, Andrew
3. System:
    - UI: Williams, Samuel
    - Backend
        - Database: Samuel, Williams
        - API:
            - ML_api (demad, travel_time, stops): Andrew, Adobea, Samuel
            - Assignment_api (vehicle_assignment): Samuel, Andrew




## Authors
Below are the contributors to the project:

- [Andrew](https://github.com/kojomensahonums)
- [Adobea]()
- [William]()
- [Samuel Amihere](https://github.com/SamuelAmihere)