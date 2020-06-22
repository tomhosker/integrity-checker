""" This code holds a class which walks through the two file trees, comparing
their respective folders and files. """

# Standard imports.
import filecmp
import os
import pathlib
import time

# Constants.
IDENTICAL_CODE = 1
MISSING_FROM_FIRST_CODE = 2
MISSING_FROM_SECOND_CODE = 3
NOT_IDENTICAL = 5

##############
# MAIN CLASS #
##############

class Comparator:
    """ The class in question. """
    def __init__(self, first_root, second_root):
        self.first_root = first_root
        self.second_root = second_root
        self.cwd = CWD()
        self.completed_folders = []
        self.completed_folders_second = []
        self.missing_from_first = []
        self.missing_from_second = []
        self.not_identical = []

    def all_sub_folders_completed(self, rel_path):
        """ Check if we've already gone through all the subfolder in the
        current directory. """
        abs_path = self.first_root+rel_path
        folders = os.listdir(abs_path)
        for folder in folders:
            if os.path.isdir(abs_path+folder):
                folder_path = rel_path+folder
                if folder_path not in self.completed_folders:
                    return False
        return True

    def walk_through(self):
        """ Walk through each directory in the tree. """
        path_to_here = self.first_root+"/"+self.cwd.get_path()
        files_and_folders = os.listdir(path_to_here)
        for filename in files_and_folders:
            if os.path.isfile(path_to_here+filename):
                self.compare_file(filename)
        if (self.cwd.is_root() and
            self.all_sub_folders_completed(self.cwd.get_path())):
            return
        for folder in files_and_folders:
            path_to_folder = path_to_here+folder
            if os.path.isdir(path_to_folder):
                if path_to_folder not in self.completed_folders:
                    self.cwd.change_down(folder)
                    self.walk_through()
        self.completed_folders.append(self.cwd.get_path())
        self.cwd.change_up()
        self.walk_through()

    def compare_file(self, filename):
        """ Compare the two versions of a given file. """
        first_abs_path = self.first_root+self.cwd.get_path()+filename
        second_abs_path = self.second_root+self.cwd.get_path()+filename
        if not os.path.exists(second_abs_path):
            self.missing_from_second.append(first_abs_path)
        elif not filecmp.cmp(first_abs_path, second_abs_path,
                             shallow=False):
            self.not_identical.append(first_abs_path)

    def write_report(self):
        """ Write a report on the integrity of the data. """
        epoch_str = str(int(time.time()))
        path_to_report = (str(pathlib.Path.home())+"/integrity_report_"+
                          epoch_str+".txt")
        report = ("Report on file trees "+self.first_root+" and "+
                  self.second_root+" at "+epoch_str)
        report_code = self.get_report_code()
        if report_code == IDENTICAL_CODE:
            report = report+"\n\nGood news! File trees are identical."
        elif report_code%MISSING_FROM_FIRST_CODE == 0:
            report = (report+"\n\nThe following files are absent in the "+
                      "first tree, but present in the second:\n\n    ")
            for item in self.missing_from_first:
                if self.missing_from_first.index(item):
                    report = report+item
                else:
                    report = report+", "+item
        elif report_code%MISSING_FROM_SECOND_CODE == 0:
            report = (report+"\n\nThe following files are absent in the "+
                      "second tree, but present in the first:\n\n    ")
            for item in self.missing_from_second:
                if self.missing_from_second.index(item):
                    report = report+item
                else:
                    report = report+", "+item
        elif report_code%NOT_IDENTICAL == 0:
            report = (report+"\n\nThe following files are present in both "+
                      "trees, but are not identical:\n\n    ")
            for item in self.not_identical:
                if self.not_identical.index(item):
                    report = report+item
                else:
                    report = report+", "+item
        with open(path_to_report, "w") as report_file:
            report_file.write(report)
        print("Report written to "+path_to_report+".")

    def get_report_code(self):
        """ Calculate a code, indicating the status of the report. """
        result = IDENTICAL_CODE
        if len(self.missing_from_first) > 0:
            result = result*MISSING_FROM_FIRST_CODE
        if len(self.missing_from_second) > 0:
            result = result*MISSING_FROM_SECOND_CODE
        if len(self.not_identical) > 0:
            result = result*NOT_IDENTICAL
        return result

    def walk_and_write(self):
        """ Walk through the file trees and write the report. """
        self.walk_through()
        self.write_report()

################################
# HELPER CLASSES AND FUNCTIONS #
################################

class CWD:
    """ A helper class which keeps track of what folder we're in, in BOTH
    file trees. """
    def __init__(self):
        self.folders = []

    def change_down(self, folder):
        """ Change directory to a sub-folder. """
        self.folders.append(folder)

    def change_up(self):
        """ Move up in the file tree. """
        if len(self.folders) == 0:
            raise Exception("Nowhere else to go!")
        last_index = len(self.folders)-1
        self.folders.remove(self.folders[last_index])

    def reset(self):
        """ Go back to the root. """
        self.folders = []

    def is_root(self):
        """ Ronseal. """
        if len(self.folders) == 0:
            return True
        else:
            return False

    def get_path(self):
        """ Print out a path for our current working directory, relative to
        the two roots. """
        result = ""
        for folder in self.folders:
            result = result+folder+"/"
        return result

###########
# TESTING #
###########

def test0():
    """ Run the first test. """
    home_dir = str(pathlib.Path.home())+"/"
    first_root = home_dir+"integrity-checker/test_files/test0/first_root/"
    second_root = home_dir+"integrity-checker/test_files/test0/second_root/"
    cmptr = Comparator(first_root, second_root)
    assert cmptr.get_report_code() == IDENTICAL_CODE

def test():
    """ Run the unit tests. """
    test0()
    print("Tests passed!")

def demo():
    """ Run a demo. """
    home_dir = str(pathlib.Path.home())+"/"
    first_root = home_dir+"integrity-checker/test_files/test0/first_root/"
    second_root = home_dir+"integrity-checker/test_files/test0/second_root/"
    cmptr = Comparator(first_root, second_root)
    cmptr.walk_and_write()

###################
# RUN AND WRAP UP #
###################

def run():
    """ Ronseal. """
    test()

if __name__ == "__main__":
    run()
