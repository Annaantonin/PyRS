"""
File manager for instrument geometry calibration files generated by instrument scientists dated from day-1 of
PyRS starts to commission.
"""


class CalibrationManager(object):
    """
    A class to handle all the calibration files
    calibration shall be related to date (run cycle), wave length and etc
    """
    def __init__(self,  calib_lookup_table_file=None):
        """
        initialization for calibration manager
        :param calib_lookup_table_file: calibration table file to in order not to scan the disk and save time
        """
        self._cal_dict = dict()  # dict[wavelength, date] = param_dict
                                 # param_dict[motor position] = calibrated value

        return

    def get_calibration(self, ipts_number, run_number):
        """ get calibration in memory
        :param ipts_number:
        :param run_number:
        :return:
        """
        return

    def locate_calibration_file(self, ipts_number, run_number):
        """

        :param ipts_number:
        :param run_number:
        :return:
        """
        return

    def show_calibration_table(self):
        """

        :return:
        """


# END-DEF-CLASS (CalibrationManager)
