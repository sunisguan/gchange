import requests as rq
import time
import hmac
import base64
import json
import hashlib
import re

class SerRe(object):
    # 网络访问返回值，包括：dict, status
    def __init__(self, res: dict, success: bool):
        self.res = res
        self.s = success


class BTCCService(object):
    access_key = "26a5a3c0-5aab-4315-8326-28fc154905ee"
    secret_key = "9478bc4f-835d-440c-bf77-6ee96057934b"
    baseUrl = "https://api.btcchina.com/api_trade_v1.php"

    # get_account_info params
    GET_ACCOUNT_INFO_PARAMS = {'ALL': 'all', 'Fronze': 'fronze', 'Balance': 'balance', 'Loan': 'loan', 'Profile': 'profile'}

    def __init__(self):
        pass

    def _get_tonce(self):
        return int(time.time()*1000000)

    def _get_params_hash(self, pdict):
        pstring = ""
        # The order of params is critical for calculating a correct hash
        fields = ['tonce','accesskey','requestmethod','id','method','params']
        for f in fields:
            if pdict[f]:
                if f == 'params':
                    # Convert list to string, then strip brackets and spaces
                    # probably a cleaner way to do this
                    param_string = re.sub("[\[\] ]","",str(pdict[f]))
                    param_string = re.sub("'",'',param_string)
                    param_string = re.sub("True",'1',param_string)
                    param_string = re.sub("False",'',param_string)
                    param_string = re.sub("None",'',param_string)
                    pstring += f + '=' + param_string + '&'
                else:
                    pstring += f + '=' + str(pdict[f]) + '&'
            else:
                pstring += f + '=&'
        pstring = pstring.strip('&')

        # now with correctly ordered param string, calculate hash
        phash = hmac.new(bytearray(self.secret_key, 'utf-8'), bytearray(pstring, 'utf-8'), hashlib.sha1).hexdigest()
        return phash

    def _request(self, post_data):
        tonce = self._get_tonce()
        post_data['tonce'] = tonce
        post_data['accesskey'] = self.access_key
        post_data['requestmethod'] = 'post'

        if not 'id' in post_data:
            post_data['id'] = tonce
            
        pd_hash = self._get_params_hash(post_data)

        # must use b64 encode        
        auth_string = base64.b64encode(bytearray(self.access_key+':'+pd_hash, 'utf-8'))
        auth_string = 'Basic ' + auth_string.decode('utf-8')
        headers = {'Authorization':auth_string,'Json-Rpc-Tonce':tonce}
        
        post_data = json.dumps(post_data)

        resp = rq.post(self.baseUrl, headers = headers, data = post_data)

        if resp.ok:
            resp_dict = json.loads(resp.text)
            #resp_dict = json.dumps(json.loads(response.read()))
 
            # The id's may need to be used by the calling application,
            # but for now, check and discard from the return dict

            if str(resp_dict['id']) == str(json.loads(post_data)['id']):
                if 'result' in resp_dict:
                    res = resp_dict['result']
                    #print('=======>>>>>> http response result = {}'.format(res))
                    return SerRe(res, True)
                elif 'error' in resp_dict:
                    return SerRe(resp_dict['error'], False)
        else:
            # not great error handling....
            print("status:",resp.status_code)
            print("reason:",resp.reason)
 
        return None

    def get_account_info(self, type = None):
        # type: GET_ACCOUNT_INFO_PARAMS, None == all
        post_data = {}
        post_data['method'] = 'getAccountInfo'
        post_data['params'] = [] if not type else [type]
        return self._request(post_data)

    