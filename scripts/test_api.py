import urllib.request
import json

base = 'http://81.71.44.180:8080/dgear'
endpoints = [
    ('GET', '/api/indicator/tree', None),
    ('GET', '/api/indicator-item/list', None),
    ('GET', '/api/indicator-result/list?startDate=2023-01-01&endDate=2023-12-31', None),
]

for method, path, body in endpoints:
    url = base + path
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read().decode('utf-8')
            data = json.loads(raw)
            code = data.get('code')
            d = data.get('data')
            dtype = type(d).__name__
            dlen = len(d) if isinstance(d, (list, dict)) else '-'
            msg = str(data.get('message', ''))[:60]
            print('[OK]  ' + method + ' ' + path.split('?')[0] + ' => code=' + str(code) + ' data_type=' + dtype + ' len=' + str(dlen) + ' msg=' + msg)
    except Exception as e:
        print('[ERR] ' + method + ' ' + path.split('?')[0] + ' => ' + str(e))

# Test POST calculate
print()
print('--- Testing POST calculate ---')
import urllib.parse
calc_url = base + '/api/indicator-result/calculate'
params = {
    'metricCode': '',
    'timeDimension': 'YEAR',
    'startDate': '2023-01-01',
    'endDate': '2023-12-31'
}

# First get a leaf metric code from tree
try:
    req = urllib.request.Request(base + '/api/indicator/tree')
    with urllib.request.urlopen(req, timeout=10) as r:
        tree_data = json.loads(r.read().decode('utf-8'))
    
    def find_leaf(nodes):
        for n in nodes:
            if n.get('isLeaf') == 1:
                return n.get('metricCode')
            children = n.get('children', [])
            if children:
                result = find_leaf(children)
                if result:
                    return result
        return None
    
    leaf_code = find_leaf(tree_data.get('data', []))
    print('Found leaf metric code: ' + str(leaf_code))
    
    if leaf_code:
        calc_params = urllib.parse.urlencode({
            'metricCode': leaf_code,
            'timeDimension': 'YEAR',
            'startDate': '2023-01-01',
            'endDate': '2023-12-31'
        })
        req2 = urllib.request.Request(calc_url + '?' + calc_params, data=b'', method='POST')
        req2.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req2, timeout=30) as r:
            raw = r.read().decode('utf-8')
            data = json.loads(raw)
            print('[OK]  POST /calculate => code=' + str(data.get('code')) + ' data=' + str(data.get('data'))[:100] + ' msg=' + str(data.get('message',''))[:60])
except Exception as e:
    print('[ERR] POST /calculate => ' + str(e))
