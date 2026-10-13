# Individual Contribution Report

## Student Information

- Name: HALA M. E. ALHIBI
- Student ID: 2509115179
- GitHub Username: halaalhibi
- Project: Smart File Manager

## Contributions

I worked on the filtering part of the Smart File Manager project. My contribution focused on creating and improving functions that check whether a file matches specific rules from the configuration file.

### Extension Filter

I implemented the `extension_filter` function. This function checks whether a file has a required extension, such as `pdf`, `jpg`, or `png`.

It extracts the file extension from the path, removes the dot, converts it to lowercase, and compares it with the required extension. It supports both one extension and multiple extensions.

Example: `extension_filter("report.pdf", "pdf")` returns `True`.

### Name Filter

I implemented the `name_filter` function. This function checks whether a file name matches a specific pattern.

It extracts only the file name from the full path and uses `fnmatch` to support wildcard patterns such as `IMG_*`, `Screenshot*`, and `*.pdf`.

Example: `name_filter("IMG_1234.jpg", "IMG_*")` returns `True`.

### Size Filter

I implemented the `size_filter` function. This function checks whether a file matches a size condition.

It checks if the path is a real file, gets the file size using `os.path.getsize()`, converts the size from bytes to megabytes, and compares it with conditions such as `greater_than` and `less_than`.

Example: `size_filter("video.mp4", {"greater_than": 500})` checks whether the file is larger than 500 MB.

### Age Filter

I implemented the `age_days_filter` function. This function checks how old a file is based on its last modification date.

It gets the file modification time, calculates the file age in days, and compares it with conditions such as `greater_than` and `less_than`.

Example: `age_days_filter("old_file.pdf", {"greater_than": 30})` checks whether the file is older than 30 days.

### Content Text Filter

I added the `contains_text_filter` function. This function checks whether a text file contains a specific word or phrase.

It opens the file, reads the content using UTF-8 encoding, converts both the content and searched text to lowercase, and checks if the searched text exists inside the file.

Example: `contains_text_filter("README.md", "Smart File Manager")` returns `True` if the phrase exists in the file.

## Error Handling

I added error handling and input validation to make the filters more reliable.

The filters handle invalid input, empty values, missing files, unreadable files, invalid paths, and invalid size values. Instead of crashing the program, the functions return `False` when the input is invalid or the file cannot be processed.

## Matcher Integration

I connected the filters to the `MATCHERS` dictionary so the program can call the correct function based on the rule written in the JSON configuration file.

For example, when the configuration contains `"extension": "pdf"`, the program uses `extension_filter`.

I also added `contains_text` to the matcher system so the new content filter can be used by the project.

## Configuration Update

I updated `config.py` to include `contains_text` as a valid filter.

This allows the configuration file to accept rules that search inside text files.

## Testing

I tested the new content filter with `README.md` using the phrase `Smart File Manager`.

The test returned `True`, which confirmed that the function can read a file and detect text inside it.

## Summary

My work focused on the filtering system of the Smart File Manager project. I implemented filters for file extension, file name, file size, file age, and file content. I also added error handling, matcher integration, configuration support, and testing for the new content-based filter.
