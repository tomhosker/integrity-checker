# Integrity Checker

This is a short Python program, which checks the integrity of data stored in a file tree.

It requires the following:

* A Linux-based operating system;
* Two distinct file trees, each of which is *supposed* to hold a perfect copy of the data we are try to preserve.

It works as follows:

1. The user provides the paths of the two file trees mentioned above, and starts the program.
1. The program walks through each folder and file of the first tree, comparing each to its equivalent in the second tree.
1. The program walks through each folder and file of the second tree, looking for anything present in the second tree but absent in the first.
1. The program finishes by producing a short report on the above.
