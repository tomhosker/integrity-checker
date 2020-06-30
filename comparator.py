""" This code holds a class which walks through the two file trees, comparing
their respective folders and files. """

# Standard imports.
import filecmp
import os
import pathlib
import shutil
import time

# Constants.
WHOLLY_IDENTICAL_CODE = 1
MISSING_FROM_FIRST_CODE = 2
MISSING_FROM_SECOND_CODE = 3
DIFF_EQUIVALENT_FILES_CODE = 5

##############
# MAIN CLASS #
##############

class Comparator:
    """ The class in question. """
    def __init__(self, first_root, second_root):
        self.first_root = first_root
        self.second_root = second_root
        self.cwd = CWD()
        self.completed_folders = set()
        self.completed_folders_second = set()
        self.missing_from_first = set()
        self.missing_from_second = set()
        self.diff_equivalent = set()

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

    def all_sub_folders_completed_second(self, rel_path):
        """ Check if we've already gone through all the subfolder in the
        current directory. """
        abs_path = self.second_root+rel_path
        folders = os.listdir(abs_path)
        for folder in folders:
            if os.path.isdir(abs_path+folder):
                folder_path = rel_path+folder
                if folder_path not in self.completed_folders_second:
                    return False
        return True

    def walk_through(self):
        """ Walk through each directory in the tree. """
        path_to_here = combine_path(self.first_root, self.cwd.get_path())
        files_and_folders = os.listdir(path_to_here)
        for filename in files_and_folders:
            if os.path.isfile(combine_path(path_to_here, filename)):
                self.compare_file(filename)
        if (self.cwd.is_root() and
                self.all_sub_folders_completed(self.cwd.get_path())):
            return
        for folder in files_and_folders:
            path_to_folder_rel = self.cwd.get_path()+folder
            path_to_folder_abs = path_to_here+folder
            if os.path.isdir(path_to_folder_abs):
                if path_to_folder_rel not in self.completed_folders:
                    self.cwd.change_down(folder)
                    self.walk_through()
        self.completed_folders.add(self.cwd.get_path())
        self.cwd.change_up()
        self.walk_through()

    def walk_through_second(self):
        """ Walk through each directory in the SECOND tree. """
        path_to_here = combine_path(self.second_root, self.cwd.get_path())
        files_and_folders = os.listdir(path_to_here)
        for filename in files_and_folders:
            if os.path.isfile(combine_path(path_to_here, filename)):
                self.compare_file(filename)
        if (self.cwd.is_root() and
                self.all_sub_folders_completed_second(self.cwd.get_path())):
            return
        for folder in files_and_folders:
            path_to_folder_rel = self.cwd.get_path()+folder
            path_to_folder_abs = path_to_here+folder
            if os.path.isdir(path_to_folder_abs):
                if path_to_folder_rel not in self.completed_folders_second:
                    self.cwd.change_down(folder)
                    self.walk_through_second()
        self.completed_folders_second.add(self.cwd.get_path())
        self.cwd.change_up()
        self.walk_through_second()

    def walk_through_both(self):
        """ Walk through both file trees. """
        self.walk_through()
        self.walk_through_second()

    def compare_file(self, filename):
        """ Compare the two versions of a given file. """
        first_abs_path = combine_path(self.first_root, self.cwd.get_path())
        first_abs_path = combine_path(first_abs_path, filename)
        second_abs_path = combine_path(self.second_root, self.cwd.get_path())
        second_abs_path = combine_path(second_abs_path, filename)
        if not os.path.exists(first_abs_path):
            self.missing_from_first.add(second_abs_path)
        elif not os.path.exists(second_abs_path):
            self.missing_from_second.add(first_abs_path)
        elif not filecmp.cmp(first_abs_path, second_abs_path,
                             shallow=False):
            self.diff_equivalent.add(first_abs_path)

    def write_report(self):
        """ Write a report on the integrity of the data. """
        epoch_str = str(int(time.time()))
        path_to_report = (str(pathlib.Path.home())+"/integrity_report_"+
                          epoch_str+".txt")
        report = ("Report on file trees "+self.first_root+" and "+
                  self.second_root+" at "+epoch_str)
        report_code = self.get_report_code()
        if report_code == WHOLLY_IDENTICAL_CODE:
            report = report+"\n\nGood news! File trees are identical."
        if report_code%MISSING_FROM_FIRST_CODE == 0:
            report = (report+"\n\nThe following files are absent in the "+
                      "first tree, but present in the second:\n\n    ")
            for item in self.missing_from_first:
                report = report+item+", "
            if report.endswith(", "):
                report = report[:-2]
        if report_code%MISSING_FROM_SECOND_CODE == 0:
            report = (report+"\n\nThe following files are absent in the "+
                      "second tree, but present in the first:\n\n    ")
            for item in self.missing_from_second:
                report = report+item+", "
            if report.endswith(", "):
                report = report[:-2]
        if report_code%DIFF_EQUIVALENT_FILES_CODE == 0:
            report = (report+"\n\nThe following files are present in both "+
                      "trees, but are not identical:\n\n    ")
            for item in self.diff_equivalent:
                report = report+item+", "
            if report.endswith(", "):
                report = report[:-2]
        with open(path_to_report, "w") as report_file:
            report_file.write(report)
        print("Report written to "+path_to_report+".")

    def get_report_code(self):
        """ Calculate a code, indicating the status of the report. """
        result = WHOLLY_IDENTICAL_CODE
        if len(self.missing_from_first) > 0:
            result = result*MISSING_FROM_FIRST_CODE
        if len(self.missing_from_second) > 0:
            result = result*MISSING_FROM_SECOND_CODE
        if len(self.diff_equivalent) > 0:
            result = result*DIFF_EQUIVALENT_FILES_CODE
        return result

    def walk_and_write(self):
        """ Walk through the file trees and write the report. """
        self.walk_through_both()
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
            return
        last_index = len(self.folders)-1
        self.folders.remove(self.folders[last_index])

    def reset(self):
        """ Go back to the root. """
        self.folders = []

    def is_root(self):
        """ Ronseal. """
        if len(self.folders) == 0:
            return True
        return False

    def get_path(self):
        """ Print out a path for our current working directory, relative to
        the two roots. """
        result = ""
        for folder in self.folders:
            result = combine_path(result, folder)
        return result

def combine_path(left, right):
    """ Combine two snippets of a path. """
    if left == "":
        result = right
    elif left.endswith("/"):
        result = left+right
    else:
        result = left+"/"+right
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
    cmptr.walk_through_both()
    assert cmptr.get_report_code() == WHOLLY_IDENTICAL_CODE

def test1():
    """ Run the next test. """
    home_dir = str(pathlib.Path.home())+"/"
    first_root = home_dir+"integrity-checker/test_files/test1/first_root/"
    second_root = home_dir+"integrity-checker/test_files/test1/second_root/"
    cmptr = Comparator(first_root, second_root)
    cmptr.walk_through_both()
    assert cmptr.get_report_code() == MISSING_FROM_FIRST_CODE

def test2():
    """ Run the next test. """
    home_dir = str(pathlib.Path.home())+"/"
    first_root = home_dir+"integrity-checker/test_files/test2/first_root/"
    second_root = home_dir+"integrity-checker/test_files/test2/second_root/"
    cmptr = Comparator(first_root, second_root)
    cmptr.walk_through_both()
    assert cmptr.get_report_code() == MISSING_FROM_SECOND_CODE

def test3():
    """ Run the next test. """
    home_dir = str(pathlib.Path.home())+"/"
    first_root = home_dir+"integrity-checker/test_files/test3/first_root/"
    second_root = home_dir+"integrity-checker/test_files/test3/second_root/"
    cmptr = Comparator(first_root, second_root)
    cmptr.walk_through_both()
    assert cmptr.get_report_code() == DIFF_EQUIVALENT_FILES_CODE

def test4():
    """ Run the next test. """
    home_dir = str(pathlib.Path.home())+"/"
    first_root = home_dir+"integrity-checker/test_files/test4/first_root/"
    second_root = home_dir+"integrity-checker/test_files/test4/second_root/"
    cmptr = Comparator(first_root, second_root)
    cmptr.walk_through_both()
    assert cmptr.get_report_code() == WHOLLY_IDENTICAL_CODE

def test5():
    """ Run the next test. """
    home_dir = str(pathlib.Path.home())+"/"
    first_root = home_dir+"integrity-checker/test_files/test5/first_root/"
    second_root = home_dir+"integrity-checker/test_files/test5/second_root/"
    cmptr = Comparator(first_root, second_root)
    cmptr.walk_through_both()
    assert cmptr.get_report_code() == MISSING_FROM_FIRST_CODE

def test6():
    """ Run the next test. """
    home_dir = str(pathlib.Path.home())+"/"
    first_root = home_dir+"integrity-checker/test_files/test6/first_root/"
    second_root = home_dir+"integrity-checker/test_files/test6/second_root/"
    cmptr = Comparator(first_root, second_root)
    cmptr.walk_through_both()
    assert cmptr.get_report_code() == MISSING_FROM_SECOND_CODE

def test7():
    """ Run the next test. """
    home_dir = str(pathlib.Path.home())+"/"
    first_root = home_dir+"integrity-checker/test_files/test7/first_root/"
    second_root = home_dir+"integrity-checker/test_files/test7/second_root/"
    cmptr = Comparator(first_root, second_root)
    cmptr.walk_through_both()
    assert cmptr.get_report_code() == DIFF_EQUIVALENT_FILES_CODE

def test8():
    """ Run the next test. """
    home_dir = str(pathlib.Path.home())+"/"
    first_root = home_dir+"integrity-checker/test_files/test8/first_root/"
    second_root = home_dir+"integrity-checker/test_files/test8/second_root/"
    cmptr = Comparator(first_root, second_root)
    cmptr.walk_through_both()
    assert cmptr.get_report_code() == WHOLLY_IDENTICAL_CODE

def test9():
    """ Run the next test. """
    home_dir = str(pathlib.Path.home())+"/"
    first_root = home_dir+"integrity-checker/test_files/test9/first_root/"
    second_root = home_dir+"integrity-checker/test_files/test9/second_root/"
    cmptr = Comparator(first_root, second_root)
    cmptr.walk_through_both()
    all_errors = (MISSING_FROM_FIRST_CODE*MISSING_FROM_SECOND_CODE*
                  DIFF_EQUIVALENT_FILES_CODE)
    assert cmptr.get_report_code() == all_errors

def basic_tests():
    """ Ronseal. """
    test0()
    test1()
    test2()
    test3()

def middle_tests():
    """ Ronseal. """
    test4()
    test5()
    test6()
    test7()

def higher_tests():
    test8()
    test9()

def test():
    """ Run the unit tests. """
    print("Extracting test files...")
    os.system("unzip test_files.zip >/dev/null")
    print("Running tests...")
    basic_tests()
    middle_tests()
    higher_tests()
    print("Tests passed!")
    shutil.rmtree("test_files/")

def demo():
    """ Run a demonstration. """
    print("Extracting test files...")
    os.system("unzip test_files.zip >/dev/null")
    print("Running demonstration...")
    home_dir = str(pathlib.Path.home())+"/"
    first_root = home_dir+"integrity-checker/test_files/test9/first_root/"
    second_root = home_dir+"integrity-checker/test_files/test9/second_root/"
    cmptr = Comparator(first_root, second_root)
    cmptr.walk_and_write()
    shutil.rmtree("test_files/")

###################
# RUN AND WRAP UP #
###################

def run():
    """ Ronseal. """
    #test()
    demo()

if __name__ == "__main__":
    run()
