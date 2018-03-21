# coding: utf-8

from hashlib import md5


def sign():
    secret = '2b90de0f1f88eaf49593f1d827b19c63'
    secret = 'DFA84B10B7ACDD25'

    params = 'channel=0&timestamp=1521603117809&isfood=0&sellerid=11&shopid=9230&distinctId=F912A666-918C-422A-9E5C-71A7A27DC92C&lat=40.042393&platform=ios&cityid=2&deviceid=82F28B12-9DEA-49E3-9575-0EBF2A3B7EF9&pickself=0&lng=116.378677&v=4.3.3.45'
    params = ''.join(sorted(params.split('&'), reverse=True))
    s = '{}{}'.format(params, secret)

    print md5(s).hexdigest()


if __name__ == '__main__':
    sign()
