__Author__ = "Peter Herman"
__Project__ = "misc_tools"
__Created__ = "August 06, 2019"


import requests

def githubimport(user, repo, module):
   d = {}
   url = 'https://raw.githubusercontent.com/{}/{}/master/{}'.format(user, repo, module)
   print(url)
   print(requests.get(url).text)
   exec(r, d)
   return url



url = githubimport('peter-herman', 'misc_tools', 'other/TeXTable.py')

r = requests.get('https://raw.githubusercontent.com/peter-herman/misc_tools/master/other/TeXTable.py', timeout=120)
hold = requests.get('https://www.usitc.gov/publications/332/working_papers/ecwp-2019-07-b.txt', timeout=5).text

