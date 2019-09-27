import ZSZQ
from pprint import pprint

api=ZSZQ.api('1320011172','******')
api.login()
pprint(api.get_SystemMessage())
