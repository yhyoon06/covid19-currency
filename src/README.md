# project-crypto-group16

## Install InfluxDB

Import the public key used for accessing package management system

	sudo curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -


Create a list file for influxdb
	
	sudo echo "deb https://repos.influxdata.com/ubuntu bionic stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
	sudo apt-get update
	sudo apt install -y influxdb

Start and enable the service to start on boot up:
	
	sudo systemctl enable --now influxdb

Verify the influxdb service
	
	sudo systemctl status influxdb
	
## Configure the influxDB database

Edit the /etc/influxdb/influxdb.conf using the any editor, nano is shown below
	
	sudo nano /etc/influxdb/influxdb.conf
	
Modify the http section in influxdb.conf file

```YAML
[http]
  # Determines whether HTTP endpoint is enabled.
  enabled = true

  # Determines whether the Flux query endpoint is enabled.
  # flux-enabled = false

  # Determines whether the Flux query logging is enabled.
  # flux-log-enabled = false

  # The bind address used by the HTTP service.
  bind-address = ":8086"

  # Determines whether user authentication is enabled over HTTP/HTTPS.
  auth-enabled = true
```

Open the port 8086 in AWS EC2 instance VPC security inbound rules for remote access: https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html
	
Restart the influxdb 
	
	sudo systemctl restart influxdb
	
Type the following command to create user and passwd

	curl -XPOST "http://localhost:8086/query" --data-urlencode "q=CREATE USER admin WITH PASSWORD 'type_password_here' WITH ALL PRIVILEGES"

## set up (using linux or mac)

create a virtual environment: ```python3 -m venv cc```

activate it: ```source cc/bin/activate```

install required packages: ```pip install -r requirements.txt```


##  get polygon.io data
- pull data using below command (note: must have polygon.io key)
  ```python3 -c 'from customPolygonAPI import bigPull;
  bigPull(key="", multiplier=1, timespan="hour",
  start="2021-01-01", end="2021-04-01")'

- open load-influx.py and enter database credentials at the bottom of document
  ```nvim load-influx.py```
  
- change into the data director
  ```cd crypto_forex_data```
  
- convert data into json new line separated format
  ```for f in *.json; do python3 ../newline_converter.py "$f"; done```
  
- load influxDB
  ```for f in *; do python3 ../load-crypto-forex-influx.py "$f"; done```

