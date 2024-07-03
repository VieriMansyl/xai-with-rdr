'''
PrecedentValueError happens when the total precedents in RDR is greater than 
the total number of available features.
'''
class PrecedentValueError(Exception):
    pass