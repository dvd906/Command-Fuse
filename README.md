# Command-Fuse
Generates commands from the provided datasheet and command files for automations

## What for?
If you need to type a lot of commands in CLI then this is for you. 
1. You just create a datasheet as the parameters and a command file separetly
2. Add a column with 'CMD' in the datasheet and specify which commands want to generate
3. The output is the generated commands

# Usage and help
## Datasheet file
Contains all the required data for the command.
Use a 'CMD' column which holds all the commands to generate.

## Commands file
This file includes all the commands which you want to generate.
Use the following syntax:
  cmd_id \[separator\] command
  cmd_id: it will search as the command to execute
  \[separator\]: which separates the cmd_id and the command
  
## Help message
If you miss something command-fuse will help you with an error message.
In the message it will be specified the error type and the message.
