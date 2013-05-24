from random import choice


def generate_secret_key(filename):
	secret_key_file = open(filename, 'w')
	secret_key_file.write('SECRET_KEY = \'' + ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)]) + '\'\n')
	secret_key_file.close()
