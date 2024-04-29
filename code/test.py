from typing import Dict, Any

a = {
  'var1': 1,
  'var2': 2,
  'var3': "hi"
}

b = {
  'var1': 1,
  'var2': None,
  'var3': "hi",
  'var4': 4,
  'var5': 5
}

def iterDic(dic: Dict[str, Any]):
  for key, value in dic.items():
    print(f'{key}: {value}')

# iterDic(a)


def compareDic(dic1: Dict[str, Any], dic2: Dict[str, Any]):
  for key, value in dic1.items():
    if key in dic2:
      if dic2[key] != value:
        return False
    else:
      return False
  return True

# print(compareDic(a, b))


# class Node:
#   def __init__(self, value) -> None:
#     self.data = value
#     self.next = None
  
#   def setNext(self, node) -> None:
#     self.next = node
  
#   def __str__(self):
#     currNode = self
#     while currNode is not None:
#       print(currNode.data)
#       currNode = currNode.next
#     return ''

# rootA = Node(1)
# rootB = Node(2)
# rootC = Node(3)
# rootD = Node(4)
# rootA.setNext(rootB)
# rootB.setNext(rootC)
# rootC.setNext(rootD)

# print(rootA)


rule = {
  'var1': 1,
  'var2': .234,
  'var3': "hi",
  'var4': [4],
}

inputcase = {
  'var1': 1,
  'var2': 2.34,
  'var4': [4],
  'var5': 5
}

from numbers import Number

def evaluate(rule: Dict[str, Any], input_case: Dict[str, Any]):
  isValid = True
  for key, value in rule.items():
    # [ASSUMPTION] : the key in <rule> is always exist in <input case>
    try:
      input_value = input_case[key]
      print(f"ada {key} [{type(input_value)}]")

      if (value is Number) and (input_value <= value):
        isValid = False
      elif input_value != value:
        isValid = False
    except:
      print(f"tak ada {key}")
  
  print(isValid)

# evaluate(rule, inputcase)


from rdr import RDR
from node import Node


root = Node(isRoot=True)

case1 = {
  'var1': 1,
  'var2': 2,
  'var3': "hi"
}
case2 = {
  'var1': 1,
  'var2': 2,
  'var3': "hi",
  'var4': 4,
  'var5': 5
}
case3 = {
  'var1': 1,
  'var2': 2,
  'var3': "hello",
  'var4': 4
}
case4 = {
  'var1': 1,
  'var2': 2,
  'var3': "hello",
  'var4': 5,
}
case5 = {
  'var1': 1,
  'var2': 2,
  'var3': "hi",
  'var4': 5
}

case6 = {
  'var1': 1,
  'var2': 2,
  'var3': "hi",
  'var4': 5,
  'var5': 5
}

# rdr = RDR(root)
# rdr._inference_(case1, "A")
# rdr._inference_(case2, "B")
# rdr._inference_(case3, "C")
# rdr._inference_(case4, "D")
# rdr._inference_(case5, "E")
# rdr._inference_(case3, "F")
# print(rdr)

# rdr._inference_(case6, "G")
# print(rdr)


def disjoint(cornerstone: Dict[str, Any], input_case: Dict[str, Any]) -> Dict[str, Any]:
		attributes = {}
		cornerstone = cornerstone
		try:
			if cornerstone is not None:
				for key in input_case:
					if key not in cornerstone:
						attributes[key] = input_case[key]
					elif key in cornerstone and input_case[key] != cornerstone[key]:
						attributes[key] = input_case[key]
		except KeyError:
			pass

		print(f'Attributes: {attributes}')

		return attributes

dict_a = {'a': 1, 'b': 2, 'c': 3, 'd': 5}
dict_b = {'a': 1, 'b': 2, 'c': "hihihi", 'e': 4, 'f': 6}

# result = disjoint(dict_a, dict_b)
# print(result)

arr = list([1,2,3])
arr2 = [1,2,3]
arr3 = list
arr4 = list([1,2])

if (arr is not None):
  print('ada')

if (arr):
  print('ada')

if (not arr):
  print('tidak ada')

print(arr == arr2)

print(arr3, arr4)