# XAI-WITH-RDR

**Author**: Vieri Mansyl  
**Co-Author**: Windy Gambetta  

**Paper**: To Be Announced (TBA)

## Overview

This repository contains the implementation of Explainable AI (XAI) using the Single Classification Ripple Down Rule (SCRDR) algorithm. The implementation is broken down into the following components:

1. **rule.py**: Defines the `Rule` class.
2. **node.py**: Defines the `Node` class, including the disjoint function and evaluation logic.
3. **rdr.py**: The main class that handles all interactions between the user and the SCRDR system, including inference, explanation generation, and visualization of the explanations.

## How to Use RDR-XAI

### Prerequisites

- An original classification model must be pre-built.
- A prediction dataset (i.e. a training dataset used to generate the model's predictions and to understand its behavior) must be available.

### Steps

1. Define the RDR object by configuring its hyperparameters.
2. Use the `fit()` function to train the RDR model.
3. To generate an explanation for a specific instance, use the `explain_instance()` function.

## License and Usage

This repository is **open-source** and is intended primarily for **educational** and **research purposes**. Users are encouraged to explore and learn from the code to further their understanding of Explainable AI and the SCRDR algorithm. Contributions and improvements are welcomed to advance the field and foster collaboration.


## Acknowledgment

This work was partially supported by the Research, Community Service, and Innovation program (Penelitian, Pengabdian kepada Masyarakat dan Inovasi, P2MI) at the Bandung Institute of Technology. The authors would like to express their gratitude to everyone who provided valuable support throughout the research process.

## Main References
P. Compton, & B.H. Kang, *Ripple-Down Rules: the Alternative to Machine Learning*, CRC Press (Taylor and Francis), 2021, pp. 23-29.