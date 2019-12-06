"""
This module generates reduction summary for user in plain text CSV file
"""
from pyrs.core.peak_profile_utility import EFFECTIVE_PEAK_PARAMETERS  # TODO get from the first peak collection

# Default summary titles shown in the CSV file
DEFAULT_HEADER_TITLES = [('IPTS number', 'ipts'),
                         ('Run', 'run'),
                         ('Scan title', 'title'),
                         ('Sample name', 'sample_name'),
                         ('Item number', 'item_number'),
                         ('HKL phase', 'hkl'),
                         ('Strain direction', 'strain_dir'),
                         ('Monochromator setting', 'mono_set'),
                         ('Calibration file', 'cal_file'),
                         ('Hidra project file', 'project'),
                         ('Manual vs auto reduction', 'reduction')]

# Default field for values
DEFAULT_BODY_TITLES = [
    ('sub-run', 'sub_run'),
    ('vx', 'vx'),
    ('vy', 'vy'),
    ('vz', 'vz'),
    ('sx', 'sx'),
    ('sy', 'sy'),
    ('sz', 'sz'),
    ('phi', 'phi'),
    ('chi', 'chi'),
    ('omega', 'omega'),
    ('2theta', '2theta'),
    ('S1 width', 'Unknown'),
    ('S1 height', 'Unknown'),
    ('S1 Distance', 'Unknown'),
    ('Radial distance', 'Unknown')]


class SummaryGenerator(object):
    """
    Generate summary to user about peak

    Format is like

    Header:
      # IPTS number
      # Run
      # Scan title
      # Sample name
      # Item number
      # HKL phase
      # Strain direction
      # Monochromator setting (such as Si111... for wave length)
      # Calibration file, Hidra project file
      # Manual vs auto reduction
    Body:
      sub-run, vx, vy, vz, sx, sy, sz, phi, chi, omega, 2theta, S1 width, S1 height, S1 Distance, Radial distance,
      effective peak parameters

    """
    def __init__(self, filename, header_titles=None, log_list=None):
        """Initialization

        Parameters
        ----------
        filename: str
            Name of the ``.csv`` file to write
        header_titles : List of 2-tuples
            Ordered list of 2-tuple (as parameter titles and field in namedtuple for values) written in
            CSV header. The default is :py:obj:`DEFAULT_HEADER_TITLES`
        header_values : ~collections.namedtuple
            Containing value
        """
        # Check input
        # self._check_header_title_value_match(header_title, header_values)

        # Set
        if header_titles is None:
            self._header_titles = DEFAULT_HEADER_TITLES
        else:
            self._header_titles = header_titles
        if log_list is None:
            self._sample_log_list = DEFAULT_BODY_TITLES
        else:
            self._sample_log_list = log_list

        if not filename:
            raise RuntimeError('Failed to supply output filename')
        self._filename = str(filename)
        if not self._filename.endswith('.csv'):
            raise RuntimeError('Filename "{}" must end with ".csv"'.format(self._filename))

        self._constant_logs = list()

        # To write
        self._fit_engine = None
        self._header_info_section = None
        self._header_log_section = None
        self._body_section = None

    def setHeaderInformation(self, headervalues):
        '''This creates a string to write to the file without actually writing it'''
        # Reset the information
        self._header_info_section = ''

        for label, value_name in self._header_titles:
            value = headervalues.get(value_name, '')
            if value:
                line = ' = '.join((label, str(value)))
            else:
                line = label
            self._header_info_section += '# {}\n'.format(line)

    def write_csv(self, sample_logs, peak_collections, sep=',', tolerance=1E-10):
        """Export the CSV file

        Parameters
        ----------
        sep: str
            string to separate fields in the body of the file
        tolerance : float
            relative tolerance of variance to treat a sample log as a constant value
            and bring into extended header
        """
        # verify the same number of subruns everywhere
        for peak_collection in peak_collections:
            _, subruns, _, _, _ = peak_collection.get_effective_parameters_values()
            if not sample_logs.matching_subruns(subruns):
                raise ValueError('Subruns from sample logs and peak {} do not match'.format(peak_collection.peak_tag))

        # header has already been put together
        with open(self._filename, 'w') as handle:
            handle.write(self._header_info_section)
            self._write_header_constants(handle, sample_logs, tolerance)  # TODO use separator and constants
            self._write_column_names(handle, sample_logs, peak_collections)  # TODO use constants
            self._write_data(handle, sample_logs, peak_collections)  # TODO use separator and constants

    def _write_header_constants(self, handle, sample_logs, tolerance):
        """Write only the sample logs that are constants into the header. These should not appear in the body.
        """
        self._constant_logs = sample_logs.constant_logs(tolerance)  # cache value
        for name in self._constant_logs:
            handle.write('# {} = {:.5g} +/- {:.2g}\n'.format(name, sample_logs[name].mean(), sample_logs[name].std()))

    def _write_column_names(self, handle, sample_logs, peak_collections):
        # the header line from the sample logs
        column_names = [name for name in sample_logs.keys()
                        if name not in self._constant_logs]

        # the contribution from each peak
        for peak_collection in peak_collections:
            tag = peak_collection.peak_tag  # name of the peak
            # values first
            for param in EFFECTIVE_PEAK_PARAMETERS:
                column_names.append('{}_{}'.format(tag, param))
            # errors after values
            for param in EFFECTIVE_PEAK_PARAMETERS:
                column_names.append('{}_{}_error'.format(tag, param))
            column_names.append('{}_chisq'.format(tag))

        # subrun number goes in the very front
        column_names.insert(0, 'sub-run')

        handle.write(','.join(column_names) + '\n')

    def _write_data(self, handle, sample_logs, peak_collections):
        column_names = [name for name in sample_logs.keys()
                        if name not in self._constant_logs]

        for i in range(len(sample_logs.subruns)):
            line = []

            # sub-run goes in first
            line.append(str(sample_logs.subruns[i]))

            # then sample logs
            for name in column_names:
                line.append(str(sample_logs[name][i]))  # get by index rather than subrun

            for peak_collection in peak_collections:
                _, _, fit_cost, values, errors = peak_collection.get_effective_parameters_values()
                for j in range(values.shape[0]):  # number of parameters
                    line.append(str(values[j, i]))
                for j in range(errors.shape[0]):  # number of parameters
                    line.append(str(errors[j, i]))
                line.append(str(fit_cost[i]))

            handle.write(','.join(line) + '\n')
