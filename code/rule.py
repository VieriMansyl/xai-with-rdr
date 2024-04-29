from typing import Dict, Any

class Rule:
	def __init__(
		self,
		precedent: Dict[str, Any] = None,
		antecedent: Any = None,
	) -> None:
		self.precedent = precedent
		self.antecedent = antecedent

	def __str__(self) -> str:
		return f'[{self.precedent}] -> {self.antecedent}'
	
	def __repr__(self) -> str:
		return f'[{self.precedent}] -> {self.antecedent}'
	
	''' SETTER '''
	def setPrecedent(self, precedent: Dict[str, Any]) -> None:
		self.precedent = precedent
	
	def setAntecedent(self, antecedent: Any) -> None:
		self.antecedent = antecedent
	
	''' GETTER '''
	def getPrecedent(self) -> Dict[str, Any]:
		return self.precedent
	
	def getAntecedent(self) -> Any:
		return self.antecedent