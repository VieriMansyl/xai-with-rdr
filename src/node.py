from typing import Dict, Any, Tuple, Union
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
	
	'''
	function to evaluate the input_case against the node's rule:
		IF key is not in categorical_attr
			IF value is numeric
				GET operator in spe_op (if any, else use comp_op)
				IF input value is not fulfilled by the operator
				ELSE current numeric attribute has no specified operator && input value is fulfilled by the comparison operator (PRECEDENT is FULFILLED)
			ELIF input value is not equal to value -> current attribute is not numeric
			ELSE current attribute is not numeric && input value is equal to value (PRECEDENT is FULFILLED)
		ELSE current attribute is categorical
			IF input value is not equal to value
			ELSE input value is equal to value (PRECEDENT is FULFILLED)
	'''
	def _evaluate_(
		self,
		input_case: Dict[str, Any],
		comp_op: str,
		spe_op: Dict[str, str],
		categorical_attr=list
	) -> Tuple[bool, list[Dict[str, Any]]]:

		if self.isRoot:
			return True, None
		
		# comparison function for numeric attributes
		comparison = {
			'<=': lambda x, y: x <= y,
			'>=': lambda x, y: x >= y,
			'<': lambda x, y: x < y,
			'>': lambda x, y: x > y,
		}

		precedents = self.rule.getPrecedent()

		log = []
		isFulfilled = True

		for key, value in precedents.items():
			try:
				input_value = input_case[key]
				operator = ''
				fulfilled = True

				if key not in categorical_attr:
					if isinstance(value, Number):
						operator = spe_op.get(key, comp_op)
						if not comparison[operator](input_value, value):
							isFulfilled = False
							fulfilled = False
					elif input_value != value:
						isFulfilled = False
						fulfilled = False

				else:
					if input_value != value:
						isFulfilled = False
						fulfilled = False

				log.append({"key": key, "value": value, "comp": operator, "Fulfilled": fulfilled})
	
			except KeyError:
				return False, [{"There is no such condition on input_case": key}]
		
		return isFulfilled, log
	
	# function to find different attributes in input_case against node's cornerstone case
	def _disjoint_(self, input_case: Dict[str, Any]) -> Dict[str, Any]:
		attributes = {}
		cornerstone = self.cornerstone

		try:
			if cornerstone != {}:
				for key in input_case:
					if key not in cornerstone:
						attributes[key] = input_case[key]
					elif key in cornerstone and input_case[key] != cornerstone[key]:
						attributes[key] = input_case[key]
			elif self.isRoot:
				return input_case
		except KeyError:
			pass

		return attributes