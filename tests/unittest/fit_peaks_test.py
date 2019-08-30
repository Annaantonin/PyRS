#!/user/bin/python
# Test class and methods implemented for peak fitting
import os
import numpy
from pyrs.core import pyrscore
from pyrs.core import instrument_geometry
from pyrs.utilities import script_helper
from matplotlib import pyplot as plt
from pyrs.utilities import rs_project_file


class PeakFittingTest(object):
    """
    Class to test peak fitting related classes and methods
    """
    def __init__(self, input_file_name):
        """ Initialization
        :param input_file_name: name of testing HIDRA project file
        """
        # Create calibration control
        self._reduction_controller = pyrscore.PyRsCore()

        # Load data
        self._project_name = 'NFRS2 Peaks'
        hd_ws = self._reduction_controller.load_hidra_project(input_file_name, project_name=self._project_name,
                                                              load_detector_counts=False,
                                                              load_diffraction=True)

        # set wave length
        hd_ws.set_wave_length(1.071, False)

        return

    def fit_pseudo_voigt(self):
        """
        Fit pseudo-voigt peaks
        :return:
        """
        peak_info_dict = {'Fe111': {'Center': 94.5, 'Range': [91., 97]}}

        # Fit peaks
        self._reduction_controller.fit_peaks(self._project_name, sub_run_list=None,
                                             peak_type='PseudoVoigt', background_type='Linear',
                                             peaks_fitting_setup=peak_info_dict)

        return

    def fit_gaussian(self):
        """ Test fitting with Gaussian
        :return:
        """
        peak_info_dict = {'Fe111': {'Center', 84., 'Range', [70., 95]}}

        # Fit peaks
        self._reduction_controller.fit_peaks(self._project_name, sub_run_list=None,
                                             peak_type='Gaussian', background_type='Linear',
                                             peaks_fitting_setup=peak_info_dict)

        return

    def show_fit_result(self):
        """ Get the fit results and plot
        :return:
        """
        # TODO - #81 NOW - Implement get_peak_fitting_result()
        peak_name_list, peak_params_matrix = \
            self._reduction_controller.get_peak_fitting_result(self._project_name, return_format=numpy.ndarray,
                                                               effective_parameter=False)
        # Plot peak width
        sub_run_vec = peak_params_matrix[:, 0]
        peak_width = peak_params_matrix[:, 5]  # rs_project_file.HidraConstants.Peak_FWHM for pandas output
        plt.plot(sub_run_vec, peak_width, color='red', label='FWHM')

        # plt.show()

        # Test to get the original data and fitted data from
        exp_data_set = self._reduction_controller.get_diffraction_data(self._project_name, sub_run=3, mask=None)
        fit_data_set = self._reduction_controller.get_modeled_data(self._project_name, sub_run=3)

        plt.plot(exp_data_set[0], exp_data_set[1], color='black', label='Experiment')
        plt.plot(fit_data_set[0], fit_data_set[1], color='green', label='Fitted')
        plt.show()

        # Effective parameters
        peak_params_dict = self._reduction_controller.get_peak_fitting_result(self._project_name,
                                                                              return_format=dict,
                                                                              effective_parameter=True)

        # Print parameters
        print ('sub-run = {}, peak width = {}'.format(3, peak_params_dict[3]['PeakWidth']))


        return

    def save_fit_result(self, out_file_name, peak_tag):

        # Save result with default value on file name to import from and export to
        self._reduction_controller.save_peak_fit_result(self._project_name, out_file_name, peak_tag)

        return


def main():
    """
    Test main
    :return:
    """
    test_project_file_name = 'tests/testdata/Hydra_16-1_cor_log.hdf5'

    # TODO - #81 NOW - Find wave length and put to a proper place in both Hidra project file and Hidra workspace

    # Create tester
    tester = PeakFittingTest(test_project_file_name)
    # fit
    tester.fit_pseudo_voigt()
    # save
    tester.save_fit_result(test_project_file_name, 'Si111')
    # show result
    tester.show_fit_result()

    # fit for gaussian
    tester.fit_gaussian()
    tester.show_fit_result()

    # TODO - #81 NOW - More tests
    # 1. get the best fit and plot
    # 2. get the worst fit and plot
    # 3. plot all peak center
    # 4. plot all mixing factor
    # 5. plot all peak width

    return


if __name__ == '__main__':
    main()

