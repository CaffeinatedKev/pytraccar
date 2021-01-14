from pytraccar.api import TraccarAPI

traccar = TraccarAPI('https://gps01.sitesense.no')


login = traccar.login_with_token('0fiHy1qGJuyNPECfY4TeRuPeG1on4U2A')
# device = traccar.get_devices('id', '1')
# print(device)
# device = traccar.get_devices()
# print(device)
# car_values = []
# cars = []
# for car in device:
#     if car['name'] == 'SiteSense CHR':
#         car_values.append(car['id'])
#         car_values.append(car['name'])
#         car_values.append(car['status'])
#         car_values.append(car['lastUpdate'])
# print(car_values)
#
# for car in device:
#     car_id = car['id']
#     car_name = car['name']
#     car_status = car['status']
#     car_last_update = car['lastUpdate']
#     print(car_id)
#     print(car_name)
#     print(car_status)
#     print(car_last_update)


report = traccar.get_trips('deviceId', '1', 'from', '2021-01-01T18:30:00Z', 'to', '2021-01-13T18:30:00Z')
print(report)