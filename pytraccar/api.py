import requests
import json
from pytraccar.exceptions import (
    TraccarApiException,
    BadRequestException,
    ObjectNotFoundException,
    ForbiddenAccessException,
    InvalidTokenException,
    UserPermissionException
)


class TraccarAPI:
    """Traccar v4.2 - https://www.traccar.org/api-reference/
    Abstraction for interacting with Traccar REST API.

    """

    def __init__(self, base_url):
        """
        Args:
            base_url: Your traccar server URL.

        Examples:
            TraccarAPI('https://mytraccaserver.com'),
            TraccarAPI('http://1.2.3.4')
        """
        self._token = ''
        self._urls = {
            'devices': base_url + '/api/devices',
            'session': base_url + '/api/session',
            'geofences': base_url + '/api/geofences',
            'notifications': base_url + '/api/notifications',
            'reports/events': base_url + '/api/reports/events',
            'reports/trips': base_url + '/api/reports/trips',
        }
        self._session = requests.Session()

    @property
    def token(self):
        """ """
        return self._token

    """
    ----------------------
    /api/session 
    ----------------------
    """
    def login_with_credentials(self, username, password):
        """Path: /session
        Creates a new session with user's credentials.

        Args:
            username: User email
            password: User password

        Returns:
            json: Session info

        Raises:
            ForbiddenAccessException: Wrong username or password.
            TraccarApiException:

        """
        path = self._urls['session']
        data = {'email': username, 'password': password}
        req = self._session.post(url=path, data=data)

        if req.status_code == 200:
            return req.json()
        elif req.status_code == 401:
            raise ForbiddenAccessException
        else:
            raise TraccarApiException(info=req.text)

    def login_with_token(self, token):
        """Path: /session
        Creates a new session by using the provided token.

        Args:
          token: User session token.
                 This token can be generated on the web interface.

        Returns:
          json: Session info

        Raises:
            InvalidTokenException:
            TraccarApiException:

        """
        path = self._urls['session']
        data = {'token': token}
        req = self._session.get(url=path, params=data)

        if req.status_code == 200:
            self._token = token  # Save valid token.
            return req.json()
        elif req.status_code == 404:
            raise InvalidTokenException
        else:
            raise TraccarApiException(info=req.text)

    """
    ----------------------
    /api/devices 
    ----------------------
    """
    def get_all_devices(self):
        """Path: /devices
        Can only be used by admins or managers to fetch all entities.

        Args:

        Returns:
          json: All users devices

        """
        path = self._urls['devices']
        data = {'all': True}
        req = self._session.get(url=path, params=data)

        if req.status_code == 200:
            return req.json()
        if req.status_code == 400:
            raise UserPermissionException
        else:
            raise TraccarApiException(info=req.text)

    def get_devices(self, query=None, params=None):
        """
        Path: /devices
        Fetch a list of devices.
        Without any params, returns a list of the user's devices.

        Args:
          query: Fetch by: userId, id or uniqueId (Default value = None)
          params: identifier or identifiers list.
            Examples: [5, 10], 'myDeviceID' (Default value = None)

        Returns:
          json: Device list

        Raises:
          ObjectNotFoundException:

        """
        path = self._urls['devices']

        data = {query: params}
        req = self._session.get(url=path, params=data)

        if req.status_code == 200:
            return req.json()
        elif req.status_code == 400:
            raise ObjectNotFoundException(obj=params, obj_type='Device')
        else:
            raise TraccarApiException(info=req.text)

    def create_device(self, name, unique_id, group_id=0,
                      phone='', model='', contact='', category=None):
        """Path: /devices
        Create a device. Only requires name and unique ID.
        Other params are optional.

        https://www.traccar.org/api-reference/#/definitions/Device

        Args:
          name: Device name.
          unique_id: Device unique identifier.
          group_id: Group identifier (Default value = 0)
          phone: Phone number (Default value = None)
          model: Device model (Default value = None)
          contact: (Default value = None)
          category: Device type (Optional)
            Arrow, Default, Animal, Bicycle, Boat, Bus, Car, Crane,
            Helicopter, Motorcycle, Offroad, Person, Pickup, Plane,
            Ship, Tractor, Train, Tram, Trolleybus, Truck, Van

        Returns:
          json: Created device.

        Raises:
          BadRequestException: If device exists in database.

        """

        path = self._urls['devices']

        data = {
            "id": -1,  # id auto-assignment
            "name": name,
            "uniqueId": unique_id,
            "phone": phone,
            "model": model,
            "contact": contact,
            "category": category,
            "groupId": group_id,
        }

        req = self._session.post(url=path, json=data)

        if req.status_code == 200:
            return req.json()
        elif req.status_code == 400:
            raise BadRequestException(message=req.text)
        else:
            raise TraccarApiException(info=req.text)

    def update_device(self, device_id, name=None, unique_id=None, group_id=None,
                      phone=None, model=None, contact=None, category=None):

        # Get current device values
        req = self.get_devices(query='id', params=device_id)
        device_info = req[0]

        update = {
            'name': name,
            'uniqueId': unique_id,
            'phone': phone,
            'model': model,
            'contact': contact,
            'category': category,
            'groupId': group_id,
        }

        # Replaces all updated values in device_info
        data = {key: value if update.get(key) is None else update[key] for key, value in device_info.items()}
        headers = {'Content-Type': 'application/json'}

        req = self._session.put('{}/{}'.format(self._urls['devices'], device_id),
                                data=json.dumps(data), headers=headers)

        if req.status_code == 200:
            return req.json()
        elif req.status_code == 400:
            raise BadRequestException(message=req.text)
        else:
            raise TraccarApiException(info=req.text)

    def delete_device(self, device_id):
        req = self._session.delete('{}/{}'.format(self._urls['devices'], device_id))

        if req.status_code != 204:
            raise TraccarApiException(info=req.text)


    """
    ----------------------
    /api/notifications
    ----------------------
    """
    def get_all_notifications(self):
        """Path: /notifications
        Can only be used by admins or managers to fetch all entities

        Args:

        Returns:
          json: list of Notifications

        """
        path = self._urls['notifications']
        data = {'all': True}
        req = self._session.get(url=path, params=data)

        if req.status_code == 200:
            return req.json()
        elif req.status_code == 400:
            raise UserPermissionException
        else:
            raise TraccarApiException(info=req.text)

    def get_trips(self, q1=None, p1=None, q2=None, p2=None, q3=None, p3=None):

        path = self._urls['reports/trips']

        data = {q1: p1, q2: p2, q3: p3}
        print(data)
        req = self._session.get(url=path, params=data)

        if req.status_code == 200:
            return req.json()
        else:
            raise TraccarApiException(info=req.text)