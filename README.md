# Automata-based Detection of Network Anomalies

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
(<source state> <destination state> <symbol> <probability>)*
(<final state> <probability>)*
```

### Tool Support

All tools in the suite works with automata obtained from a list of messages
(packets) divided into *conversations* (messages that logically belong
together). Messages (packets) are assumed to be provided in a csv file (each
message per line). Files containing message are then input of the tools below.
Messages are splitted into conversations based on a particular protocol (an
incomplete parser for IEC 104 is provided).


Tools are located in the directory `src`.
- `anomaly_member.py` Tool for a detection of anomalies in a csv file (testing
  file) based on a given valid traffic sample (training file). Based on the
  particular method, a PA/PTA is first obtained from training file. The
  detection mechanism then checks whether conversations from testing file
  (divided into time windows) all belongs to language of the learned PA/PTA
  (i.e., each conversation has nonzero probability).
- `anomaly_distr.py` Tool for a detection of anomalies in a csv file (testing
  file) based on a given valid traffic sample (training file). Based on the
  particular method, a PA/PTA is first obtained from training file. The
  detection mechanism then checks whether, for each time window from the testing
  file, the Euclid distance of a PA/PTA obtained from that window with the
  PA/PTA obtained from the training file is below a threshold.
- `pa_learning.py` Learning of PAs based on own implementation of Alergia
  (including the testing phase). As an input it takes a csv file containing
  messages.
- `pta_learning.py` Learning of PAs based on prefix trees--PTAs (including the
  testing phase). As an input it takes a csv file containing messages.

### Structure of the Repository

- `src` Source codes of the tool support
