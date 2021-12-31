import os
from collections import defaultdict

def return_secret(file_path=r'C:\Users\Atsuya\PycharmProjects\pythonProject\TwitterScraping\secrets'):
    secret_dict = defaultdict(str)
    with open(file_path, 'r', encoding='utf-8') as f:
        secrets = f.readlines()
    for secret in secrets:
        key, value = secret.strip('\n').split('=')
        secret_dict[key] = value
    return secret_dict