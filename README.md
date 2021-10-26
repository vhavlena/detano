# Automata-based Detection of Network Anomalies

Detano toolsuite is tailored for learning probabilistic automata (Alergia
algorithm with extensions) and anomaly detection in ICS networks based on
probabilistic automata.

### Installation

To run the tools you need to have installed Python 3 with the following packages
- dataclasses
- bidict
- bitarray
- numpy
- scipy
- FAdo for Python 3

These packages you can install using the `pip3` util. Or you can use the
provided `requirements.txt` file (all dependencies can be installed via `pip3
install -r requirements.txt`). In order to generate the documentation run
`doxygen` in the `doc` folder.

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
- `anomaly_check.py` Tool for a detection of anomalies in a csv file (testing
  file) based on a given valid traffic sample (training file). Based on the
  particular method, a PA/PTA is first obtained from training file. The
  detection mechanism then checks whether conversations differs from the testing
  file. Currently supported approaches include detection based on comparing
  distributions and detection based on single conversation reasoning.
- `pa_learning.py` Learning of PA based on own implementation of Alergia
  (including the testing phase) and learning based on prefix trees (PTAs). As an
  input it takes a csv file containing messages.

Supporting rules are placed in directory `units` (run with
`python3 -m units.conv_splitter <params>`).
- `window_extract.py` Extract conversations from a give range of time windows.
  The script takes a .csv file together with the number of the first and the last
  window, and returns parsed conversations belonging to each window.


### Anomaly Detection

The anomaly detection approaches implemented within the tool `anomaly_check.py`
takes as an input a file capturing valid network traffic and a file containing
traffic to be inspected. Examples of csv input files can be found in [Dataset
repository](https://github.com/matousp/datasets). More specifically, detection
approaches (based on distribution comparison or single conversation reasoning)
can be run as follows:

- `anomaly_check.py <valid csv file> <inspected csv file> [OPT]` where
  `OPT` allows the following specifications:
  * `--atype=pa/pta` learning based on PAs/PTAs (default PA)
  * `--alg=distr/member` anomaly detection based on comparing distributions
    (distr) or single message reasoning (member) (default distr)
  * `--smoothing` use smoothing (for distr only)
  * `--reduced=val` remove similar automata with the given error upper-bound val
    [0,1] (for distr only)
  * `--help` print a help message

### Automata Learning

Approaches for learning of probabilistic automata in the context of industrial
networks are implemented within the tool `pa_learning.py`. The tool takes as an
input a file capturing network traffic. Examples of csv input files can be found
in [Dataset repository](https://github.com/matousp/datasets). More specifically,
the tool can be run as follows:

- `pa_learning.py <csv file> [OPT]` where `OPT` allows the following specifications:
  * `--atype=pa/pta` learning based on PAs/PTAs (default PA)
  * `--format=conv/ipfix` format of input file: conversations/IPFIX (default IPFIX)
  * `--help` print a help message

### Structure of the Repository

- `src` Source codes of the tool support

### Citing

**Efficient Modelling of ICS Communication For Anomaly Detection Using Probabilistic Automata**. Petr Matoušek, Vojtěch Havlena, and Lukáš Holík. In
*Proceedings of IFIP/IEEE International Symposium on Integrated Network
Management*. ISBN 978-3-903176-32-4. 2021
([pdf](http://dl.ifip.org/db/conf/im/im2021/210993.pdf))

### Contact

If you have a question, do not hesitate to contact the authors:
- Vojtěch Havlena `<ihavlena at fit.vutbr.cz>`
- Petr Matoušek `<matousp at fit.vutbr.cz>`
- Lukáš Holík `<holik at fit.vutbr.cz>`
