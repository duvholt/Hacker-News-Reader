from random import choice


def generate_secret_key(filename):
    secret_key_file = open(filename, 'w')
    key = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for _ in xrange(50)])
    secret_key_file.write('SECRET_KEY = \'' + key + '\'\n')
    secret_key_file.close()
