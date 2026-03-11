For running locally on docker:
Rename .env.example to .env.
To create dependant services:
```shell
./create_dependant_services.sh
```
WARNING!
The dependencies deployment script will automatically remove containers named:
- xp-local-postgres
- xp-local-rabbit
And will create volumes named:
- xp-local-pgdata
- xp-local-rabbitmq-data

To deploy the web app:
```shell
./deploy-local.sh
```
WARNING!
The web app deployment script will automatically remove containers named:
- xp-webserver-local
