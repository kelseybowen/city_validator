import csv
import json
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

state_set = set()
city_set = set()
data_set = set()

with open('cities.csv', mode='r', newline='') as file:
    csv_reader = csv.reader(file)
    next(csv_reader, None)
    for row in csv_reader:
        data_set.add((row[0], row[1]))
        state_set.add(row[1])
        city_set.add(row[0])

while True:
    message = socket.recv()
    decoded = message.decode()
    python_object = json.loads(decoded)
    if (python_object['city'], python_object['state']) in data_set:
        message = str({
            "valid": True,
            "city": python_object["city"],
            "state": python_object["state"],
            "formatted_location": f"{python_object['city']}, {python_object['state']}"
        })
    else:
        # valid state
        if python_object['state'] in state_set:
            # valid city
            if python_object['city'] in city_set:
                # city does not exist in that state
                message = str({
                    "valid": False,
                    "error": f"{python_object['city']} does not exist in {python_object['state']}",
                    "suggestion": "Please validate your input"
                    })
            # invalid city
            else:
                message = str({
                    "valid": False,
                    "error": f"Invalid city name: {python_object['city']}",
                    "suggestion": "Please check spelling of the city and try again"
                    })
        # invalid state
        else:
            # valid city
            if python_object['city'] in city_set:
                # city does not exist in that state
                message = str({
                    "valid": False,
                    "error": f"Invalid state name: {python_object['state']}",
                    "suggestion": "Please check the spelling of the state and try again"
                    })
            # invalid city
            else:
                message = str({
                    "valid": False,
                    "error": f"Invalid city and state name: {python_object['city']}, {python_object['state']}",
                    "suggestion": "Please validate your input"
                    })
        socket.send_string(message)

context.destroy()