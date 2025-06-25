#!/usr/bin/env python

import os
import pandas as pd


def main():
    eD0_df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                      'dimpledSpheresDragData/eD0_smooth.csv'),
                         index_col=0, header=None)
    eD1p5Em3_df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                           'dimpledSpheresDragData/eD1p5e-3.csv'),
                              index_col=0, header=None)
    eD5Em3_df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                         'dimpledSpheresDragData/eD5e-3.csv'),
                            index_col=0, header=None)
    eD1p25Em2_df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                            'dimpledSpheresDragData/eD1p25e-2.csv'),
                               index_col=0, header=None)
    eD1p04Em1_df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                            'dimpledSpheresDragData/GolfBall.csv'),
                               index_col=0, header=None)

    eD0_df.columns = [0.0]
    eD1p5Em3_df.columns = [1.5e-3]
    eD5Em3_df.columns = [5e-3]
    eD1p25Em2_df.columns = [1.25e-2]
    eD1p04Em1_df.columns = [1.04e-1]

    merged_df = eD0_df.merge(eD1p5Em3_df, how='outer', left_index=True,
                             right_index=True, sort=True)
    merged_df = merged_df.merge(eD5Em3_df, how='outer', left_index=True,
                                right_index=True, sort=True)
    merged_df = merged_df.merge(eD1p25Em2_df, how='outer', left_index=True,
                                right_index=True, sort=True)
    # merged_df = merged_df.merge(eD1p04Em1_df, how='outer', left_index=True,
    #                             right_index=True, sort=True)

    # TODO (esb 2021-10-08): extend the data for the real golf ball so we can
    #                        include it.

    merged_filled_df = merged_df.interpolate(method='slinear',
                                             limit_direction='forward').dropna()

    merged_filled_df.index.name = 'Re'
    merged_filled_df.to_hdf('cd_table.h5', '/cd_table')


if __name__ == "__main__":
    main()
