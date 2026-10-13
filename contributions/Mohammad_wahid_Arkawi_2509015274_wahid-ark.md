# Individual Contribution Report

## Student Information

- Name: MOHAMMAD WAHID ARKAWI
- Student ID: 2509015274
- GitHub Username: wahif-ark
- Project: Smart File Manager

## Contributions

I worked on the rename action of the Smart File Manager project, and I also wrote the README file and prepared the project presentation.

### Rename Action

I implemented the `rename_action` function. This function renames a file using a format string, and can also move it to another folder.

It checks that the path is a real file, then replaces the placeholders `{name}`, `{date}`, `{size}` and `{extension}` in the format with the real values of the file. If a destination folder is given, the file is moved there, otherwise it stays in the same folder. If a file with the same name already exists, it adds `_1`, `_2`, etc. instead of overwriting it.

Example: `rename_action("invoice.pdf", "", "{date}_{name}.{extension}")` renames the file to `2026-10-13_invoice.pdf`.

### README

I wrote the README file. It explains the matching rules, the available actions and their options, the rename placeholders, a usage example, and important notes such as dry run and permanent deletion.

### Presentation

I prepared the project presentation, which explains what the project does and how its parts work together.

## Summary

My contribution to the Smart File Manager project was the `rename_action` function, the README file, and the project presentation. The rename action lets users rename files with a custom format and optionally move them, without overwriting existing files.