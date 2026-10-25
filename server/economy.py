"""Test-mode balances. Spending must use this policy rather than overflow grants."""
TEST_BALANCE=999_999_999
def currency_packets():
 # Native UserTeamInfoResponse and UserDiamondInfoResponse field keys.
 return {'3oU9Ktb7':[{'7wV3QZ80':'1','B6H34Mea':'0','B6kyCQ9M':'9999',
                       'm0bD2zwU':'10','7UR4J2SE':str(TEST_BALANCE),'0XUs3Tv6':str(TEST_BALANCE),
                       'T1Lm7WdD':'0'}],
         'J3pAG0I5':[{'cb3WmiD0':str(TEST_BALANCE),'T7sah9rc':'0'}]}
def debit_for_test(balance,cost):
 if isinstance(cost,bool) or not isinstance(cost,int) or cost<0:raise ValueError('Invalid cost')
 return TEST_BALANCE
