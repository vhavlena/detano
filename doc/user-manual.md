# User Manual

All tools in the suite works with probabilistic automata obtained from a list of
messages (packets) divided into *conversations* (messages that logically belong
together). Messages (packets) are assumed to be provided in a csv file (each
message per line). Files containing message are then input of the tools below.
The tools also allow to work with conversations given as an input. Currently
supported protocols are IEC 104 and MMS (if the messages are given as an input,
only IEC 104 is supported).


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

Program documentation is placed in directory `doc` (to generate the documentation
  run `doxygen` in `doc` directory).


### Input Data Format

The list of messages is assumed to be provided in an IPFIX csv file, one message per line with the following columns:
```
TimeStamp;Relative Time;srcIP;dstIP;srcPort;dstPort;ipLen;len;fmt;uType;asduType;numix;cot;oa;addr;ioa
```
As an example, see files from [Dataset
repository](https://github.com/matousp/datasets) or the following:
```
TimeStamp;Relative Time;srcIP;dstIP;srcPort;dstPort;ipLen;len;fmt;uType;asduType;numix;cot;oa;addr;ioa
15:03:10.31;0.000000;192.158.2.111;192.158.2.248;55000;2404;58;17;0x00000000;;122;1;13;0;63535;64537
15:03:10.31;0.000595;192.158.2.248;192.158.2.111;2404;55000;63;19;0x00000000;;120;1;13;0;63535;64537
```

The list of conversations is assumed to be provided in a csv file, one conversation per line, given as
```
Timestamp;Relative Time;Duration;Length;Data
Key;<src IP>-<dest IP>-<src port>-<dest port>;
```
where data is a comma separated sequence of messages. For the case of IEC 104, a message is represented by a pair `<asduType.cot>`, for the case of MMS, a message is represented by a pair `<MMStype.service>`. For instance
```
Timestamp;Relative Time;Duration;Length;Data
Key;192.158.2.100-192.158.2.101-2404-55000;
13:20:51.45;2.562578489;0.212390052;706;<100.6>,<100.7>,<1.20>,<100.10>
```


### Anomaly Detection

The anomaly detection approaches implemented within the tool `anomaly_check.py`
takes as an input a file capturing valid network traffic and a file containing
traffic to be inspected. Format of input files is described above. Examples of csv input files can be found in [Dataset
repository](https://github.com/matousp/datasets). More specifically, detection
approaches (based on distribution comparison or single conversation reasoning)
can be run as follows:

- `anomaly_check.py <valid csv file> <inspected csv file> [OPT]` where
  `OPT` allows the following specifications:
  * `--atype=pa/pta` learning based on PAs/PTAs (default PA)
  * `--alg=distr/member` anomaly detection based on comparing distributions
    (distr) or single message reasoning (member) (default distr)
  * `--format=conv/ipfix`	format of input data: conversations (conv) or csv data in ipfix format (ipfix) (default ipfix)
  * `--smoothing` use smoothing (for distr only)
  * `--reduced=val` remove similar automata with the given error upper-bound val
    [0,1] (for distr only)
  * `--threshold=val` find malicious conversations from windows having distance higher than val
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


### Example of Use

First, download datasets from [Dataset
repository](https://github.com/matousp/datasets). The benchmark contains
datasets in IPFIX format, capturing various anomaly scenarios. Example of the
anomaly detection:

```bash
$ ./anomaly_check.py ../../datasets/scada-iec104/attacks/normal-traffic.csv ../../datasets/scada-iec104/attacks/scanning-attack.csv --atype=pa --alg=distr --smoothing --format=ipfix
```
```
Automata counts:
192.168.11.248:2404 -- 192.168.11.111:61254 | 4

Detection results:
../../datasets/scada-iec104/attacks/normal-traffic.csv ../../datasets/scada-iec104/attacks/scanning-attack.csv

192.168.11.248:2404 -- 192.168.11.111:61254
0;0.0
1;0.0
2;0.0
3;0.0
4;0.0
5;0.0
6;0.0
...
```

The *Automata counts* part shows the number of automata models used for each
communication pair. The *Detection results* part then shows concrete output of
the detection for each communication pair and each time window in the testing
traffic (numbered from 0) in the form of `<window>;<detection output>`.

Example of the automata learning:

```bash
$ ./pa_learning.py ../../datasets/scada-iec104/attacks/normal-traffic.csv --atype=pa --format=ipfix
```
```
File: normal-traffic.csv
alpha: 0.05, t0: 13
States 3
Testing: 0/25233 (missclassified/all)
Accuracy: 1.0
```

The output shows used learning parameters, the number of states of the learned
DPA and the accuracy. The learning uses first 33 % of the input traffic for
learning and the rest for accuracy evaluation (this value can be changed
directly in the file `pa_learning.py`).
