import csv

config = {
    'Umrechnungsfaktor':1,
    'AnzahlMessungen':5,
    'XStart':10,
    'YStart':10,
    'XEnd':50,
    'YEnd':50,
    'DeltaX':5,
    'DeltaY':5
}
field_names = [
    'Umrechnungsfaktor',
    'AnzahlMessungen',
    'XStart',
    'YStart',
    'XEnd',
    'YEnd',
    'DeltaX',
    'DeltaY'
]

with open('config.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_names)
    writer.writeheader()
    writer.writerow(config)
