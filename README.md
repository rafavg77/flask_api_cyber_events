# flask_api_cyber_events
flask api to register groups and events related to Cybersecurity and Hacking

```bash
python3 src/main.py

#Create group
http POST :5001/group name="Grupo 1" description="Distinguido grupo de caballeros asistentes al Defcon y otros eventos"
http POST :5001/group name="Grupo 2" description="Grupo de colegas de Ciberseguridad"

#Create event
http POST :5001/event name="Defcon" description="Evento de Hacking en las Vegas" date=2023-08-13 url="https://defcon.org/\?mob\=1" group="1"http POST :5001/event name="BlackHat" description="Evento donde se presetan herramientas de Ciberseguridad & Hacking" date=2023-08-05 url="https://www.blackhat.com/us-23/" group="2"

#Get all groups
http GET :5001/groups

#Get all events
http GET :5001/events

#Get group by id
http GET :5001/group/1 

#Get events by id
http GET :5001/event/1


```

