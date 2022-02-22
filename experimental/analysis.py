#!/usr/bin/env python3

import sys
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

ATTACKS = {
  "HMI-MITM": [(118, 132)],
  "RTU-MITM": [(118, 132)],
  "HMI-replay": [(147,176), (283, 298)],
  "HMI-masquerating": [(3,63)],
  "HMI-report-block": [(123,150)],
  "HMI-value-change": [(124,147)]
}

def main():
    file = sys.argv[1]
    data = pd.read_csv(file, delimiter=";", names=["window", "value"])
    threshold = 0.2
    attacks = [] # ATTACKS["HMI-MITM"]

    data = data.dropna()
    data = data.astype({"window": int, "value": np.float16})

    higher = data[data["value"] >= threshold]

    hit = 0
    for at in attacks:
        tmp = higher[higher.apply(lambda x: x["window"] >= at[0] and x["window"] <= at[1], axis=1)]
        if tmp.shape[0] > 0:
            hit += 1

    noattack = higher[higher.apply(lambda x: all((x["window"] < l or x["window"] > r) for l,r in attacks), axis=1)]

    print("Hit: {0}".format(hit))
    print("Miss: {0}".format(len(attacks)-hit))
    print("False negatives: {0}".format(noattack.shape[0]))



if __name__ == "__main__":
    main()
