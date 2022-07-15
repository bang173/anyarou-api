import argparse
from requests import get

def make_req(method: str) -> str: 
    params = {
        'key': 'your key',
        'method': method if method else 'status'
    }
    r = get('http://0.0.0.0:5000/your/endpoint', params=params)
    return r.text

def main():
    methods = (
        'run', 'stop', 'restart', 'status', 'update', 'screens',
        'start', 'shutdown', 'upgrade'
    )
    parser = argparse.ArgumentParser(description='Console panel for Anyarou.')
    parser.add_argument('method', action='store', choices=methods)

    namespace = parser.parse_args()
    
    if (m := namespace.method) and m in methods:
        res = make_req(m)
        print(res)

if __name__ == '__main__':
    main()
