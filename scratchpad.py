import re

txt =  "aws and homo and docker node"
amazon = re.compile(r'\bamazon\b | \baws\b', flags=re.I | re.X)
print(amazon.findall(txt))

other = re.compile(r'\bterraform\b | \bdocker\b | \bansible\b', flags=re.I | re.X)
print(other.findall(txt))

node = re.compile(r'\bnodejs\b | \bnode\b', flags=re.I | re.X)
print(node.findall(txt))

if len(amazon.findall(txt)) >= 1 and  len(other.findall(txt)) >= 1 or len(node.findall(txt) >= 1):
    print("print the text")




