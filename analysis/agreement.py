#!/usr/bin/env python
import sys

import krippendorff
import pandas as pd


def main() -> None:
    df = pd.read_csv(filepath_or_buffer=sys.stdin if len(sys.argv) == 1 else sys.argv[1])
    df["votes_yes"] = df["votes_1"] + df["votes_2"] + df["votes_3"] + df["votes_4"] + df["votes_5"]

    binary = df[["votes_no", "votes_yes"]].to_numpy()
    funniness = df[["votes_1", "votes_2", "votes_3", "votes_4", "votes_5"]].to_numpy()

    print(f"alpha for humor: {krippendorff.alpha(value_counts=binary, level_of_measurement='nominal'):.4f}")
    print(f"alpha for funniness: {krippendorff.alpha(value_counts=funniness):.4f}")
    print("alpha for funniness as ordinal: "
          f"{krippendorff.alpha(value_counts=funniness, level_of_measurement='ordinal'):.4f}")
    alpha_ratio = krippendorff.alpha(value_counts=funniness, level_of_measurement='ratio', value_domain=[1, 2, 3, 4, 5])
    print(f"alpha for funniness as ratio: {alpha_ratio:.4f}")


if __name__ == "__main__":
    main()
