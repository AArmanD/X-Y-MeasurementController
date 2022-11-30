import csv

config = {
"conversion_factor":1234,
"number_of_measurement_runs":1234,
"number_of_measurements_in_one_position":1234,
"x_start_value":1234,
"y_start_value":1234,
"x_end_value":1234,
"y_end_value":1234,
"delta_x_value":1234,
"delta_y_value":1234,
}

#config = {
#    'Umrechnungsfaktor':1,
#    'AnzahlMessungen':5,
#    'XStart':10,
#    'YStart':10,
#    'XEnd':50,
#    'YEnd':50,
#    'DeltaX':5,
#    'DeltaY':5
#}
field_names = [
    "conversion_factor",
    "number_of_measurement_runs",
    "number_of_measurements_in_one_position",
    "x_start_value",
    "y_start_value",
    "x_end_value",
    "y_end_value",
    "delta_x_value",
    "delta_y_value"
]

with open('config.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_names)
    writer.writeheader()
    writer.writerow(config)
