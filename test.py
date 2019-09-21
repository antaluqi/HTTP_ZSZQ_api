import ZSZQ
import Comm

api=ZSZQ.api('1320011172','615919')
api.login()
print(api.get_balance())