import qrcode
import os
import requests

def generate_bitcoin_address():
    # Burada benzersiz bitcoin adresi oluşturma mantığı yer alacak
    bitcoin_address = '1BoatSLRHtKNngkdXEeobR76b53LETtpyT'
    private_key = '5HueCGU8rMjxEXxiPuD5BDuGb7DJdrP94K1fjfTKhfQYj6U7'
    with open('keys.txt', 'a') as f:
        f.write(f'Address: {bitcoin_address}, Private Key: {private_key}\n')
    return bitcoin_address

def get_bitcoin_balance(bitcoin_address):
    response = requests.get(f'https://blockchain.info/q/addressbalance/{bitcoin_address}')
    balance_satoshi = int(response.text)
    balance_btc = balance_satoshi / 1e8
    balance_eur = balance_btc * get_current_btc_to_eur_rate()
    return balance_eur, balance_btc

def get_current_btc_to_eur_rate():
    response = requests.get('https://api.coindesk.com/v1/bpi/currentprice/EUR.json')
    data = response.json()
    return data['bpi']['EUR']['rate_float']
