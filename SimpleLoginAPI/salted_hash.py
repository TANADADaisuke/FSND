import bcrypt

password = b"stufyhart"
password_1 = b"securepassword"
password_2 = b"udacity"
password_3 = b"learningisfun"

# Hash a password for the first time, with a certain number of rounds
salts = bcrypt.gensalt(14)
hashed = bcrypt.hashpw(password, salts)
print('salt:', salts)
print('hash:', hashed)

# password 1
hashed_1 = bcrypt.hashpw(password_1, salts)
print('hash_1:', hashed_1)

# password 2
hashed_2 = bcrypt.hashpw(password_2, salts)
print('hash_2:', hashed_2)

# password 3
hashed_3 = bcrypt.hashpw(password_3, salts)
print('hash_3:', hashed_3)
