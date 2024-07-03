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
- ran_precedent : (randomize precedent) boolean to determine if the total_precedent used will be randomized or a fixed value
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

			log_entry.append({'label': currentNode.getRule().getAntecedent()}) if (isFulfilled) else None
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
		cornerstones: Dict[str, Any] = None,
	) -> None:
		
		try:
			precedents = None

			if self._total_precedent == 0:	# use all the cases as the precedent
				precedents = cases
			elif self._total_precedent > len(cornerstones):  # check if the total_precedent is within bounds (i.e. not greater than the total number of available features)
				raise PrecedentValueError('Total precedent value is greater than the total number of available features')
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
			raise e


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


	def predict(self, X: pd.DataFrame):
		solutions = np.array([])
		for input_case in X.to_dict(orient='records'):
			output, _, _, _, _ = self._inference_(input_case)
			
			solutions = np.append(solutions, output)
		return solutions


	def change_label(
			self,
			input_case: pd.DataFrame,
			new_label: Any
		) -> None:
		case = input_case.to_dict(orient='records')[0]

		_, lastTrueNode, isFulfilled, previousNode, _ = self._inference_(case)
		refinementCases = lastTrueNode._disjoint_(case)

		if not refinementCases:
			refinementCases = lastTrueNode.getRule().getPrecedent()
		self._addRefinementNode_(isFulfilled, previousNode, refinementCases, new_label, case)


	def explain_instance(self, case):

		def group_by_key(explanations):
			grouped = {}
			label = None

			for explanation in explanations:
				if not explanation:
					continue
				for item in explanation:
					if isinstance(item, dict):
						if 'label' in item:
							label = item
							continue
						key = item.get('key')
						if key:
							if key not in grouped:
								grouped[key] = []
							grouped[key].append(item)

			result = list(grouped.values())
			return result, label
		
		if isinstance(case, pd.DataFrame):
			output, lastTrueNode, _, _, explanations = self._inference_(case.to_dict(orient='records')[0])
		elif isinstance(case, dict):
			output, lastTrueNode, _, _, explanations = self._inference_(case)
		reason = {}
		cornerstone = lastTrueNode.getCornerstone()

		precedents = lastTrueNode.getRule().getPrecedent()
		if precedents:
			for key, value in precedents.items():
				reason[key] = value

		modifiedExp = []
		label_encountered = False
		for sublist in explanations:
			if sublist and any('label' in d for d in sublist):
				if not label_encountered:
					modifiedExp.append(sublist)
					label_encountered = True
			elif not sublist:
				continue
			else:
				modifiedExp.append(sublist)
		
		groupedExp, label = group_by_key(modifiedExp)

		reasons = []
		for ex in groupedExp:
			reason = {}
			val = []

			for condition in ex:
				key = condition['key']
				value = condition['value']
				comp = condition['comp']
				isFulfilled = condition['isFulfilled']

				if not comp:	# categorical attr
					if isFulfilled:
						val = value
						break
					else:
						val.append(value) if (value not in val) else None
				else:			# numeric attr
					if isFulfilled:
						if comp == '<=' or comp == '<':
							if (not val):
								val = [None, value]
							elif (not val[1]) or (value < val[1]):
								val[1] = value
						elif comp == '>=' or comp == '>':
							if (not val):
								val = [value, None]
							elif (not val[0]) or (val[0] < value):
								val[0] = value
					else:
						if comp == '<=' or comp == '<':
							if (not val):
								val = [value, None]
							elif (not val[0]) or (val[0] < value):
								val[0] = value
						elif comp == '>=' or comp == '>':
							if (not val):
								val = [None, value]
							elif (not val[1]) or (value < val[1]):
								val[1] = value

			reasons.append({
				'key': key,
				'value': val,
				'comp': comp,
				'isFulfilled': isFulfilled
			})

		display(case) # type: ignore
		
		self.visualize_explanation(reasons, label)
		return output, reason, cornerstone


# log's item : {key, value, comp, isFulfilled}
# [{'key': 'Age', 'value': 69.0, 'comp': '<=', 'isFulfilled': True}, {'label': 'M'}]
# [{'key': 'sex', 'value': 'M', 'comp': '', 'isFulfilled': False}]
	def visualize_explanation(self, reasons, label):

		inversed_op = {
			'<=': '>',
			'>=': '<',
			'<': '>=',
			'>': '<='
		}
		
		table = []
		for reason in reasons:
			condition = ''
			key = reason['key']
			value = reason['value']
			comp = reason['comp']
			isFulfilled = reason['isFulfilled']

			if not comp:		# categorical attr
				if isFulfilled:
					# condition = f"{key} is {mappings[key][value]}" if key in mappings else f"{key} is {value}"
					condition = f"{key} is {value}"
				else:
					if isinstance(value, list):
						if len(value) == 2:
							# condition = f"{key} is neither {mappings[key][value[0]]} nor {mappings[key][value[1]]}"\
							# 			if key in mappings\
							# 			else f"{key} is neither {value[0]} nor {value[1]}"
							condition = f"{key} is neither {value[0]} nor {value[1]}"
						else:
							# condition = f"{key} are not {', '.join([mappings[key][v] for v in value])}"\
							# 			if key in mappings\
							# 			else f"{key} are not {', '.join(value)}"
							condition = f"{key} are not {', '.join(map(str, value))}"
					else:
						condition = f"{key} is not {value}"
			else:		# numeric attr
				if not isFulfilled:
					if comp == '<=' or comp == '<':
						condition = f"{key} {inversed_op[comp]} {value[0]}"
					elif comp == '>=' or comp == '>':
						condition = f"{key} {inversed_op[comp]} {value[1]}"
				else:
					if comp == '<=' or comp == '<':
						condition = f"{value[0]} < {key} {comp} {value[1]}" if value[0] else f"{key} {comp} {value[1]}"
					elif comp == '>=':
						condition = f"{value[0]} <= {key} < {value[1]}" if value[1] else f"{key} >= {value[0]}"
					elif comp == '>':
						condition = f"{value[0]} < {key} < {value[1]}" if value[1] else f"{key} > {value[0]}"
			
			table.append([condition])
		
		dff = pd.DataFrame(table, columns=['Reasons'])

		table_width = dff.shape[1] * 0.5  # Assuming each column takes up 0.5 inches
		table_height = dff.shape[0] * 0.3  # Assuming each row takes up 0.3 inches
		text_length = len(str(label['label'])) * 0.1  # Assuming each character takes up 0.1 inches
		total_width = max(table_width, text_length)  # Choose the maximum width
		total_height = table_height + 0.5  # Add some padding for the text

		fig, ax = plt.subplots(figsize=(total_width, total_height))

		# Plot the table
		tab = ax.table(
			cellText=dff.values,
			colLabels=dff.columns,
			cellLoc='center',
			loc='center'
		)

		ax.axis('off')
		tab.auto_set_column_width(col=list(range(len(dff.columns))))

		# Adjust cell alignment
		cells = tab.properties()["celld"]
		for i in range(len(dff)):
			cells[i + 1, 0].get_text().set_ha('left')

		# Get the bounding box of the table
		table_bbox = tab.get_window_extent(fig.canvas.get_renderer())

		# Convert the bounding box to figure coordinates
		inv = fig.transFigure.inverted()
		table_bbox_fig = table_bbox.transformed(inv)

		# Calculate the position for the text
		text_x = table_bbox_fig.x0  # Use the left edge of the table
		text_y = table_bbox_fig.y1 + 0.02  # 0.02 is a small offset

		# Add the prediction text right above the table, aligned to the left
		prediction_text = f"Prediction: {label['label']}"
		plt.text(text_x, text_y, prediction_text, ha='left', va='bottom', transform=fig.transFigure, fontsize=12, fontweight='bold')

		plt.show()