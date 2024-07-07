import unittest
import requests

class TestAuthEndpoint(unittest.TestCase):
    
    base_url = 'http://localhost:5000'
    
    def test_register_user_successfully(self):
        response = requests.post(f'{self.base_url}/auth/register', json={
            'firstName': 'Habeeb',
            'lastName': 'Ajayi',
            'email': 'ajayihabeeb977@gmail.com',
            'password': 'pass123'
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn('accessToken', data["data"])
        accessToken = data['data']["accessToken"]
        self.assertEqual(data['data']['user']['firstName'], 'Habeeb')
        self.assertEqual(data['data']['user']['lastName'], "Ajayi")
        self.assertEqual(data["data"]['user']["email"], "ajayihabeeb977@gmail.com")

        header = {"Authorization": "Bearer {}".format(accessToken),
                  "Content-Type": "application/json"}
        organisation_response = requests.get(f"{self.base_url}/api/organisations")

        self.assertEqual(organisation_response.status_code, 200)
        all_organisations = organisation_response.json()["data"]["organisations"]
        list_of_organ_name = []
        for organ in all_organisations:
            list_of_organ_name.append(organ["name"])
        self.assertIn("Habeeb's Organisation", list_of_organ_name)

 

    def test_login_user_successfully(self):
        response = requests.post(f'{self.base_url}/auth/login', json={
            'email': 'ajayihabeeb977@gmail.com',
            'password': 'pass123'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('accessToken', data["data"])
        self.assertEqual(data["data"]['user']['email'], 'ajayihabeeb977@gmail.com')

    def test_missing_fields(self):
        fields = ['firstName', 'lastName', 'email', 'password']
        for field in fields:
            payload = {
                'firstName': 'John',
                'lastName': 'Doe',
                'email': 'john@example.com',
                'password': 'pass123'
            }
            del payload[field]
            response = requests.post(f'{self.base_url}/auth/register', json=payload)
            self.assertEqual(response.status_code, 400)

    def test_duplicate_email(self):
        response = requests.post(f'{self.base_url}/auth/register', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'pass123'
        })
        self.assertEqual(response.status_code, 201)

        response = requests.post(f'{self.base_url}/auth/register', json={
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'pass123'
        })
        self.assertEqual(response.status_code, 422)
        self.assertIn('email', response.json()['error'])