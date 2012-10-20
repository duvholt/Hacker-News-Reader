from random import choice


def generate_secret_key(filename):
	file = open(filename, 'w')
	file.write('SECRET_KEY = \'' + ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)]) + '\'\n')
	file.close()
