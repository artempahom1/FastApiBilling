import requests
import time
import json


print('Start API test')
data1 = {
    'domain': 'wasd.com',
    'timeout_value': 8
}
res1 = requests.post('http://127.0.0.1:4201/domain_billing', json=data1)
res = requests.get('http://127.0.0.1:4201/domain_billing', params={'domain': 'wasd.com'})
print(res.text)
assert json.loads(res.text)['status']['permission'] == True
time.sleep(1)
res = requests.get('http://127.0.0.1:4201/domain_billing', params={'domain': 'wasd.com'})
print(res.text)
assert json.loads(res.text)['status']['permission'] == False
time.sleep(8)
data1 = {
    'domain': 'wasd.com',
    'timeout_value': 9
}
res1 = requests.post('http://127.0.0.1:4201/domain_billing', json=data1)
res = requests.get('http://127.0.0.1:4201/domain_billing', params={'domain': 'wasd.com'})
print(res.text)
assert json.loads(res.text)['status']['permission'] == False
data1 = {
    'domain': 'wasd.com',
    'timeout_value': 15
}
res1 = requests.post('http://127.0.0.1:4201/domain_billing', json=data1)
time.sleep(1)
res = requests.get('http://127.0.0.1:4201/domain_billing', params={'domain': 'wasd.com'})
print(res.text)
assert json.loads(res.text)['status']['permission'] == False
time.sleep(6)
res = requests.get('http://127.0.0.1:4201/domain_billing', params={'domain': 'wasd.com'})
print(res.text)
assert json.loads(res.text)['status']['permission'] == True
res = requests.delete('http://127.0.0.1:4201/domain_billing', params={'domain': 'wasd.com'})
print(res.text)
res = requests.get('http://127.0.0.1:4201/domain_billing', params={'domain': 'wasd.com'})
print(res.text)
assert json.loads(res.text)['status']['permission'] == True

print('End API test')