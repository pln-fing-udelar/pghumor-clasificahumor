#!/usr/bin/env python
import csv

import krippendorff
import numpy as np


def main() -> None:
    humor_counts = []
    funniness_counts = []
    with open("annotations_by_tweet.csv") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for _, _, _, x_str, v1_str, v2_str, v3_str, v4_str, v5_str in reader:
            x, v1, v2, v3, v4, v5 = int(x_str), int(v1_str), int(v2_str), int(v3_str), int(v4_str), int(v5_str)
            humor_counts.append([x, v1 + v2 + v3 + v4 + v5])
            funniness_counts.append([v1, v2, v3, v4, v5])

    humor_counts = np.array(humor_counts)
    funniness_counts = np.array(funniness_counts)
    print("alpha for humor: ", krippendorff.alpha(value_counts=humor_counts, level_of_measurement="nominal"))
    print("alpha for funniness: ", krippendorff.alpha(value_counts=funniness_counts))
    print("alpha for funniness as ordinal: ", krippendorff.alpha(value_counts=funniness_counts,
                                                                 level_of_measurement="ordinal"))
    print("alpha for funniness as ratio: ", krippendorff.alpha(value_counts=funniness_counts,
                                                               level_of_measurement="ratio",
                                                               value_domain=[1, 2, 3, 4, 5]))


if __name__ == "__main__":
    main()
