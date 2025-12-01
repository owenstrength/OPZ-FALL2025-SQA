# Software Quality Assurance Activities Report

## Team Members
- Owen Strength
- Parker Davis  
- Zaim Nilgiriwala

## Overview
This report documents the software quality assurance activities performed on the FAME-ML project, including fuzzing, forensics logging, and continuous integration implementation.

## Activity 4.a: Fuzzing Implementation

### Fuzzing Script (fuzz.py)
Created a comprehensive fuzzing script that automatically tests 5 key Python methods from the codebase:

1. **py_parser.getPythonParseObject** - Parses Python files into AST objects
2. **py_parser.getPythonAtrributeFuncs** - Extracts attribute function calls from AST
3. **lint_engine.getDataLoadCount** - Counts data loading events in Python files
4. **py_parser.getFunctionAssignments** - Extracts function assignment patterns
5. **py_parser.checkIfParsablePython** - Checks if a Python file can be parsed

### Fuzzing Methodology
- Generated random strings and code snippets as input
- Created temporary files with various content including valid Python, invalid syntax, and edge cases
- Implemented exception handling to catch crashes or unexpected behavior
- Tracked bugs found during fuzzing sessions

### Bugs Discovered
During fuzzing sessions, several edge cases were identified:
- Files with invalid Python syntax could trigger unexpected behavior in parsing methods
- Very large file contents could cause performance issues
- Some methods did not handle Unicode characters properly
- Error handling could be improved in some parsing functions

## Activity 4.b: Forensics Logging Implementation

### Methods Enhanced with Logging
Five Python methods were modified to include comprehensive forensics logging:

1. **lint_engine.getDataLoadCount** - Added logging for data load event detection
2. **py_parser.checkLoggingPerData** - Added logging for logging verification process
3. **py_parser.getPythonParseObject** - Added logging for file parsing operations
4. **mining.git.repo.miner.cloneRepo** - Added logging for repository cloning
5. **py_parser.getPythonAtrributeFuncs** - Added logging for attribute function extraction

### Logging Implementation Details
- Added logging.basicConfig configuration to each modified file
- Used appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- Added detailed logging messages showing function parameters, internal state, and results
- Maintained original functionality while adding comprehensive logging

### Benefits of Forensics Logging
- Improved traceability of program execution
- Better debugging capabilities
- Enhanced monitoring of security-related events
- Easier identification of processing bottlenecks

## Activity 4.c: Continuous Integration Implementation

### GitHub Actions Workflow
Created a comprehensive CI pipeline in `.github/workflows/ci.yml`:

- **Trigger**: Runs on push and pull request to main/master branches
- **Environment**: Ubuntu-latest with Python 3.9
- **Dependencies**: Installs required packages from requirements.txt
- **Tests**: Runs fuzz.py automatically as part of CI
- **Verification**: Tests main application functionality

### Requirements Management
- Created `requirements.txt` to manage project dependencies
- Includes pandas, numpy, and gitpython as required packages
- Ensures reproducible builds across environments

## Activity 4.d: Report and Lessons Learned

### Key Findings
- Fuzzing effectively identified edge cases and potential vulnerabilities
- Forensics logging provides valuable insights into code execution
- CI/CD implementation ensures consistent testing and quality assurance
- The combination of these techniques significantly improves software quality

### Technical Challenges
- Adding logging without disrupting existing functionality required careful consideration
- Fuzzing required generating diverse input sets to effectively test edge cases
- Setting up CI required managing dependencies and environment configurations

### Best Practices Applied
- Maintained backward compatibility when adding logging
- Used appropriate log levels for different types of information
- Created comprehensive fuzzing test cases covering valid and invalid inputs
- Implemented proper error handling in CI scripts

## Conclusion
The implemented SQA activities provide a robust foundation for ongoing software quality assurance. The fuzzing script will continue to identify potential issues, the forensics logging enables better monitoring and debugging, and the CI pipeline ensures quality standards are maintained with each commit.