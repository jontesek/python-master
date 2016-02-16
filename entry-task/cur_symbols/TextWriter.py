import codecs


class TextWriter(object):

    def __init__(self, output_dir='.'):
        """
        Constructor.
        :param output_dir: absolute filepath to output directory
        :return:
        """
        self.output_dir = output_dir

    def _write_file(self, data_lists, file_name, file_extension, items_delimiter, file_mode):
        # Create a file path.
        file_path = '%s/%s.%s' % (self.output_dir, file_name, file_extension)
        lines_c = len(data_lists) - 1
        # Prepare file for writing
        with codecs.open(file_path, mode=file_mode, encoding="utf-8-sig") as fh:
            # Loop through all data lists (rows).
            for line_n, line_content in enumerate(data_lists):
                # Get number of columns.
                max_index = len(line_content) - 1
                # Loop through all items in a list (row -> columns)
                for col_n in range(0, max_index+1):
                    fh.write(line_content[col_n])
                    if col_n < max_index:
                        fh.write(items_delimiter)
                # break line - not for the last item
                if line_n < lines_c:
                    fh.write('\n')

    def write_file(self, data_list, file_name, items_delimiter):
        self._write_file(data_list, file_name, 'csv', items_delimiter, 'w')
