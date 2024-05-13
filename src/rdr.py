from typing import Dict, Any
import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from rule import Rule
from node import Node
from exceptions import PrecedentValueError

'''
- precedent : the precedent of the rule
- antecedent : the antecedent of the rule
- isRoot : boolean to determine if the node is the root node
- categorical_attr : list of categorical attributes of the dataset
- total_precedent : total number of precedent in the dataset
    1 : default value
	0 : use all precedent
	n : use <n> precedent(s) (0 < n <= total features)
- ran_precedent : (randomize precedent) boolean to determine if the total_precedent used used will be randomized or a fixed value
	True : randomize the total_precedent (1 <= n <= total_precedent)
	False : use the total_precedent as is (default)
- comp_operator : (comparison operator) determine the operator for handling all numeric attributes
- spe_operator : (specified operator) determine the operator for specified numeric attributes
'''
class RDR:
	def __init__(
		self,
		precedent: Dict[str, Any] = None,
		antecedent: Any = None,
		isRoot: bool = True,
		categorical_attr=list(),
		total_precedent: int = 1,
		ran_precedent: bool = False,
		comp_operator: str = '<=',
		spe_operator: Dict[str, str] = {}
	) -> None:
		root = Node(
				Rule(precedent= precedent, antecedent= antecedent),
				isRoot= isRoot
				)
		self._root = root
		self._total_precedent = total_precedent
		self._ran_precedent = ran_precedent
		self._comp_op = comp_operator
		self._spe_op = spe_operator
		self._categorical_attr = categorical_attr


	def printRDR(
		self,
		node: Node,
		indent: int = 0,
		branch: str = ''
	) -> str:
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
		explain_log = []
		output = self._root.getRule().getAntecedent()

		while currentNode:
			
			isFulfilled, log_entry = currentNode._evaluate_(
										input_case,
										self._comp_op,
										self._spe_op,
										self._categorical_attr)    # if <rule> is fulfilled

			log_entry.append({'label': currentNode.getRule().getAntecedent()}) if (log_entry and isFulfilled) else None
			explain_log.append(log_entry)

			if isFulfilled:
				lastTrueNode = currentNode
				output = currentNode.getRule().getAntecedent()

			previousNode = currentNode
			currentNode = currentNode.getExceptNode() if isFulfilled else currentNode.getElseNode()

		
		return output, lastTrueNode, isFulfilled, previousNode, explain_log[::-1]


	def _addRefinementNode_(
		self,
		isFulfilled: bool,
		parentNode: Node,
		cases: Dict[str, Any],
		label: Any,
		cornerstones: Dict[str, Any] = None
	) -> None:
		
		try:
			precedents = None

			if self._total_precedent == 0:		# use all the cases as the precedent
				precedents = cases
			elif self._total_precedent > len(cornerstones): 		# check if the total_precedent is within bounds (i.e. not greater than the total number of available features)
				raise PrecedentValueError('PrecedentValueError: Total precedent value is greater than the total number of available features')
			else:
				precedent_items = list(cases.items())
				if self._total_precedent < len(precedent_items):  # Check if sample size is within bounds
					randomized_precedent = random.randint(1, self._total_precedent)\
						 					if self._ran_precedent\
											else self._total_precedent	# apply randomization if needed
					precedents = dict(random.sample(precedent_items, randomized_precedent))
				else:
					precedents = cases

			rules = Rule(precedent=precedents, antecedent=label)

			if isFulfilled:
				parentNode.setExceptNode(Node(rules, cornerstones))
			else:
				parentNode.setElseNode(Node(rules, cornerstones))

		except PrecedentValueError as e:
			print(e)


	def fit(self, X, y):
		# validate input
		n_samples, _ = X.shape
		if n_samples != len(y):
			raise ValueError('Number of samples in X and y must be the same')

		for i, input_case in enumerate(X.to_dict(orient='records')):
			output, lastTrueNode, isFulfilled, previousNode, _ = self._inference_(input_case)

			# validate RDR's output with the label
			input_label = y.iloc[i].values[0]

			if output != input_label:
				refinementCases = lastTrueNode._disjoint_(input_case)
				# case : if there's no different attributes between input_case and cornerstone
				if not refinementCases:
					refinementCases = lastTrueNode.getRule().getPrecedent()
				self._addRefinementNode_(isFulfilled, previousNode, refinementCases, input_label, input_case)
		
		return self


	def predict(self, X):
		solutions = np.array([])
		for input_case in X.to_dict(orient='records'):
			output, _, _, _, _ = self._inference_(input_case)
			solutions = np.append(solutions, output)

		return solutions

	
	def explain_instance(self, case):
		output, lastTrueNode, _, _, explanations = self._inference_(case.to_dict())
		reason = {}
		cornerstone = lastTrueNode.getCornerstone()

		precedents = lastTrueNode.getRule().getPrecedent()
		if precedents:
				for key, value in precedents.items():
						reason[key] = value

		self.visualize_explanation(explanations)
		return output, reason, cornerstone

# log's item : {key, value, comp, isFulfilled}
# [{'key': 'Age', 'value': 69.0, 'comp': '<=', 'isFullfilled': True}]
# [{'key': 'sex', 'value': 'M', 'comp': '', 'isFullfilled': False}]

	def visualize_explanation(self, explanations):
		inversed_op = {
			'<=': '>',
			'>=': '<',
			'<': '>=',
			'>': '<='
		}

		table = []
		for ex in explanations:
			if not ex:
				reason = 'No condition since it\'s the root node'
				label = ''
			else:
				reason = ''
				label = ''
				for id, condition in enumerate(ex):
					try:
						key = condition['key']
						value = condition['value']
						comp = condition['comp']
						fulfilled = condition['Fulfilled']

						if not comp:
							reason += f"{key} is {value}" if fulfilled else f"{key} is not {value}"
						else:
							reason += f"{key} {comp} {value}" if fulfilled else f"{key} {inversed_op[comp]} {value}"
						
						if id < len(ex) - 1:
							reason += ', '

					except KeyError:
						label = condition['label']
			table.append([reason, label])
		
		dff = pd.DataFrame(table, columns=['Reasons', 'Label'])

		_, ax = plt.subplots()

		# Plot the table
		tab = ax.table(
			cellText=dff.values,
			colLabels=dff.columns,
			cellLoc='center',
			loc='center'
		)

		ax.axis('off')
		tab.auto_set_column_width(col=list(range(len(dff.columns))))

		cells = tab.properties()["celld"]
		for i in range(len(table)):
			cells[i + 1, 0].get_text().set_ha('left')
			cells[i + 1, 1].get_text().set_ha('center')

		plt.show()