"""
interactive_repy.py --- an interactive RepyV2 console

Useful if you are tired of typing "from repyportability..." and 
"add_dy_support..." into an interactive Python prompt over and over again.

Relevant Python docs:
https://docs.python.org/2/library/code.html#code.interact

Thank you for the helpful hints:
* http://stackoverflow.com/questions/13432717/enter-interactive-mode-in-python
* http://stackoverflow.com/questions/11796474/start-interactive-mode-on-a-specific-script-line

"""

import code
import webbrowser

from repyportability import *
add_dy_support(locals())

def repy_api_help():
  webbrowser.open("https://seattle.poly.edu/wiki/RepyV2API")

code.interact(local=locals(), banner="""
Welcome to the Interactive RepyV2 console!
(Type ``repy_api_help()'' to open the Repy API documentation at 
https://seattle.poly.edu/wiki/RepyV2API in a browser window, and 
visit https://github.com/SeattleTestbed for the latest code updates.)
""")

# Once they are done, ...
print """
Thanks for using the Interactive RepyV2 console. Have a great day!"""

