# Detection of Network Anomalies

To run the tools you need to have installed Python 3 with the following packages
- bidict
- bitarray
- numpy
- scipy
- FAdo for Python 3 (install via `requirements.txt`)

These packages you can install using the `pip3` util.

### Automata Format

PAs are specified using a format, which given as follows.
```
<initial state>
<source state> <destination state> <symbol in dec> <probability>)*
(<final state> <probability>)*
```

### Tool Support

*Conversations* are assumed to be provided as a csv file (each line is a single message) where conversations are divided by an empty line (line with all fields empty). A csv file containing such divided conversations is used as an input of the tools below.

Tools are located in the directory `src`.
- `anomaly_detector.py` Tool for a detection of anomalies in a csv file based on a given probabilistic automaton. The detection mechanism cheks whether conversations provided in a csv file all belongs to language of a given PA (i.e., each conversation has nonzero probability).
- `conv_splitter.py` Tool for a splitting of a csv file into conversations (stored as described above).
- `pa_learning.py` Learning of PAs based on own implementation of Alergia (including the testing phase). As an input it takes a csv file containing conversations.
- `pta_learning.py` Learning of PAs based on prefix trees (including the testing phase). As an input it takes a csv file containing conversations.
- `euclid_distance.py` Computation of Euclid distance of two deterministic probabilistic automata. Used for a comparison of a PA representing a valid traffic with a PA representing a traffic under inspection.

### Structure of the Repository

- `src` Source codes of the tool support
