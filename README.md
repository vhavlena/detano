# Automata-based Detection of Network Anomalies

To run the tools you need to have installed Python 3 with the following packages
- dataclasses
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

### Tool Support Overview

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

Supporting rules are placed in directory `units` (run with
`python3 -m units.conv_splitter <params>`).
- `window_extract.py` Extract conversations from a give range of time windows.
  The script takes a .csv file together with the number of the first and the last
  window, and returns parsed conversations belonging to each window.


### Anomaly Detection

The anomaly detection approaches implemented within the tools `anomaly_member.py`
and `anomaly_distr.py` take as an input a file capturing valid traffic and a
file containing traffic to be inspected. Examples of csv input files can be found
on [Dataset repository](https://github.com/matousp/datasets). More specifically,
detection approaches (based on distribution comparison or single conversation
  reasoning) can be run as follows:

- `anomaly_member.py <valid csv file> <inspected csv file> <opts>` where
  `<opts>` allows the following specifications:
  * `--pa/--pta` detection is based on PAs or PTAs, respectively
- `anomaly_distr.py <valid csv file> <inspected csv file> <opts>` where
  `<opts>` allows the following specifications:
  * `--pa/--pta` detection is based on PAs or PTAs, respectively
  * `--reduced=val` remove Euclid similar automata with the threshold val


### Structure of the Repository

- `src` Source codes of the tool support
