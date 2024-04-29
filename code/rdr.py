from typing import Dict, Any
from numbers import Number
import numpy as np
from rule import Rule
from node import Node

class RDR:
	def __init__(self, root: Node, categorical_attr=list()) -> None:
		self._root = root
		self._categorical_attr = categorical_attr

	def printRDR(self, node: Node, indent: int = 0, branch: str = '') -> str:
		print(f"{' ' * indent}{'T' if branch == 'except' else 'F' if branch == 'else' else ''}>> ", end='')
		print(node)
		if node.getExceptNode():
			self.printRDR(node.getExceptNode(), indent + 4, branch='except')
		if node.getElseNode():
			self.printRDR(node.getElseNode(), indent + 4, branch='else')
		return ''

	def __str__(self) -> str:
		return self.printRDR(self._root)

	def _inference_(self, input_case: Dict[str, Any]):
		previousNode = self._root
		currentNode = self._root
		lastTrueNode = self._root
		output = self._root.getRule().getAntecedent()

		while currentNode:
			if isFulfilled := currentNode._evaluate_(input_case, self._categorical_attr):    # if <rule> is fulfilled
				lastTrueNode = currentNode
				output = currentNode.getRule().getAntecedent()

			previousNode = currentNode
			currentNode = currentNode.getExceptNode() if isFulfilled else currentNode.getElseNode()

		return output, lastTrueNode, isFulfilled, previousNode


	def _addRefinementNode_(
		self,
		isFulfilled: bool,
		parentNode: Node,
		cases: Dict[str, Any],
		label: Any,
		cornerstones: Dict[str, Any] = None
	) -> None:
		rules = Rule(precedent=cases, antecedent=label)
		if isFulfilled:
			parentNode.setExceptNode(Node(rules, cornerstones))
		else:
			parentNode.setElseNode(Node(rules, cornerstones))


	def fit(self, X, y):
		# validate input
		n_samples, _ = X.shape
		if n_samples != len(y):
			raise ValueError('Number of samples in X and y must be the same')

		for i, input_case in enumerate(X.to_dict(orient='records')):
			output, lastTrueNode, isFulfilled, previousNode = self._inference_(input_case)

			# validate RDR's output with the label
			label = y.iloc[i].values[0]

			if output != label:
				refinementCases = lastTrueNode._disjoint_(input_case)
				self._addRefinementNode_(isFulfilled, previousNode, refinementCases, label, input_case)


	def predict(self, X):
		solutions = np.array([])
		for input_case in X.to_dict(orient='records'):
			output, _, _, _ = self._inference_(input_case)
			solutions = np.append(solutions, output)

		return solutions


	def explain_instance(self, case):
		output, lastTrueNode, _, _ = self._inference_(case.to_dict())
		print(f'Output: {output}')
		print(f'Reason:')

		precedents = lastTrueNode.getRule().getPrecedent()

		if precedents:
			for key,value in precedents.items():
				if isinstance(value, Number) and (key not in self._categorical_attr):
					print(f'- {key} < {value}')
				else:
					print(f'- {key} = {value}')
		else: print("None")

		print(f'Cornerstone case: {lastTrueNode.getCornerstone()}')

		return

'''
TODO:
- build 'explain' method
- handle 'ordinal' number types -> should be handled by user during preprocessed data
'''