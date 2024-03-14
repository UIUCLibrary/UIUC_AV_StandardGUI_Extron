# UofI GUI Extron Style Guide

## Introduction

This style guide is a set of coding conventions and rules specifically for our Extron ControlScript Pro xi 1.6.10 project. It is based on the Extron's ControlScript conventions and includes some project-specific deviations and additions. The current ControlScript Pro xi Python version is 3.5.2. 

## Code Layout

1. **Indentation**: Use 4 spaces per indentation level.
2. **Line Length**: Limit all lines to a maximum of 79 characters.
3. **Blank Lines**: Surround top-level function and class definitions with two blank lines.

## Naming Conventions

1. **Variables**: Use a lowercase word or words. Separate words by underscores to improve readability.
2. **Functions**: Use a lowercase word or words. Separate words by underscores to improve readability.
3. **Classes**: Use CapWords convention.
4. **Class Methods**: Use CapWords convention. Should be in the `VerbNoun` format.
5. **Class Properties**: Use CapWords convention. Should be in the `Noun` format.

## Comments

1. **Inline Comments**: Use inline comments sparingly.
2. **Documentation Strings**: For modules, classes, functions and methods, use the `"""` triple double quotes.

## Project-Specific Guidelines

1. **Exception Handling**: Always specify the exception type in the except block.
2. **Context Managers**: Use context managers (`with` statement) for resource handling when possible.
3. **ControlScript Libraries**: Use Extron's ControlScript libraries for programming AV control system projects.
4. **Device Modules**: Use Extron's provided device modules where possible. We do not want to have to maintain too many device modules.
5. **Extended Classes**: Classes which have ben subclassed or otherwise extended should be named like `{OriginalClass}Ex`.

## Linting

Use Ruff with our project-specific configuration for linting.

## Development Tools

1. **Visual Studio Code**: Develop Extron control systems programming using Visual Studio Code.
    a) **ControlScript Extension for VS Code**: Provides ControlScript documentation and lanuage support in VS Code.  
2. **ControlScript Deployment Utility**: Use Extron's ControlScript Deployment Utility for deploying and debugging control system programs.


## Conclusion

This style guide aims to ensure that the code is easy to read and understand. Consistency with this style guide is important. Consistency within a project is more important. Consistency within one module or function is most important.