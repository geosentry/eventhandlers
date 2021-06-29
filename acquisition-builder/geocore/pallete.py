"""
Terrascope GeoCore Library

The pallete module contains visualization parameters
"""

S2TC = {'bands': ['TCI_R', 'TCI_G', 'TCI_B'], 'min': 0, 'max': 255}

NDVIRAW = {'min': 0.0, 'max': 1.0, 'palette': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
                                               '74A901', '66A000', '529400', '3E8601', '207401', '056201',
                                               '004C00', '023B01', '012E01', '011D01', '011301']}

NDVIFOCAL = {'min': 0.0, 'max': 10.0, 'palette': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
                                               '74A901', '66A000', '529400', '3E8601', '207401', '056201',
                                               '004C00', '023B01', '012E01', '011D01', '011301']}