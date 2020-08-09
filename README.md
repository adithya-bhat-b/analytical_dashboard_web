# analytical_dashboard

## Web pages

1. ### Departments page

   **URL**: ***http://{IP}:{PORT}/dashboard/departments***

2. ### Teams page

    **URL**: ***http://{IP}:{PORT}/dashboard/teams/?department_name=product***

#### [Schema diagram](https://dbdiagram.io/d/5f2ce3e908c7880b65c569e7)

## Deployment steps
### Prerequisites
1. Create postgres user

   ```
   create user postgres_user with encrypted password 'pg123';
   ```

2. Create postgres dev and prod databases

   ```
   create database dashboard;
   create database dashboard_prod;
   ```
3. Alter user to give create database role

   ```
   alter user postgres_user CREATEDB;
   grant all privileges on database dashboard to postgres_user;
   grant all privileges on database dashboard_prod to postgres_user;
   ```

4. Change the settings.dev and settings.prod database details

### Local deployment

Go to the project directory

#### Install the dependancies

```
python -m pip install -r requirements.txt
```
#### Set environment variable(for production deployment)
##### For windows
```
set ENV=PROD
```
##### For non windows
```
export ENV=PROD
```
#### Run migration
```
python manage.py migrate
```
#### Create the server
```
python manage.py runserver 0.0.0.0:{PORT}
```

> Note: Set the environment variable for only for production deployment; Default is: `dev`

### Docker deployment

#### Build the image
##### PROD
```
docker build -t dashboard --build-arg DB_ENV=prod .
```
##### DEV
```
docker build -t dashboard .
```

#### Run the image
```
docker run -d dashboard -p {PORT}:8000 -v {LOG_DIR}:/usr/app/src/analytical_dashboard/logs dashboard
```

#### Known bugs and Limitations
* Not enough debug logging
* Negative testcases were not implemented

#### What has been completed
The basic analytical dashboard APIs are done. Yet there's a room for accomodating many analytical entities.
If more time was given, would have added more analytics for other entities like users, teams etc
