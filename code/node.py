from typing import Dict, Any
from numbers import Number
from rule import Rule

class Node:
	def __init__(
		self,
		rule: Rule = None,
		case: Dict[str, Any] = {},
		isRoot: bool = False
	) -> None:
		self.rule = rule
		self.cornerstone = case
		self.exceptNode = None
		self.elseNode = None
		self.isRoot = isRoot

	def __str__(self) -> str:
		return f'[{self.rule.getPrecedent()}] -> {self.rule.getAntecedent()} | Cornerstone: {self.cornerstone}'
	
	def __repr__(self) -> str:
		return f'[{self.rule.getPrecedent()}] -> {self.rule.getAntecedent()} | Cornerstone: {self.cornerstone}'

	''' SETTER '''
	def setExceptNode(self, node: 'Node') -> None:
		self.exceptNode = node
	
	def setElseNode(self, node: 'Node') -> None:
		self.elseNode = node
	
	def setCornerstone(self, case: Dict[str, Any]) -> None:
		self.cornerstone = case
	
	''' GETTER '''
	def getExceptNode(self) -> 'Node':
		return self.exceptNode
	
	def getElseNode(self) -> 'Node':
		return self.elseNode
	
	def getRule(self) -> Rule:
		return self.rule

	def getCornerstone(self) -> Dict[str, Any]:
		return self.cornerstone
	
	# function to evaluate the input_case against the node's rule
	def _evaluate_(self, input_case: Dict[str, Any], categorical_attr=list) -> bool:
		if self.isRoot:
			return True
		
		precedents = self.rule.getPrecedent()
		
		for key, value in precedents.items():
			try:
				input_value = input_case[key]

				if (not categorical_attr) or (key not in categorical_attr):	# if categorical_attr is empty || key is not in categorical_attr
					if isinstance(value, Number) and (input_value <= value):	# implement split-point : LESS THAN OR EQUAL
						return False
					elif input_value != value:
						return False
				else:	# if categorical_attr is not empty && key is in categorical_attr {which means current attribute is categorical}
					if input_value != value:
						return False
	
			except KeyError:
				return False
		
		return True
	
	# function to find different attributes in input_case against node's cornerstone case
	def _disjoint_(self, input_case: Dict[str, Any]) -> Dict[str, Any]:
		attributes = {}
		cornerstone = self.cornerstone

		try:
			if cornerstone:
				for key in input_case:
					if key not in cornerstone:
						attributes[key] = input_case[key]
					elif key in cornerstone and input_case[key] != cornerstone[key]:
						attributes[key] = input_case[key]
		except KeyError:
			pass

		return attributes