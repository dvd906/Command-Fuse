# Command-Fuse
Generates commands from the provided datasheet and command files to executable commands for automations

## What for?
If you need to type a **lot of** commands in CLI then this is for you.
### Steps to use Command-Fuse
1. Create a datasheet (.csv, .tsv, .xlsx) as the parameters and a command file separetly (file extension is mandatory)
2. Add a column with 'CMD' in the datasheet and specify which commands want to generate
3. The output is the generated commands

# Usage and help
### 1. Datasheet file
   - Contains all the required data for the command.
   - Use a 'CMD' column which holds all the commands to generate or specify in the command
   - Columns are case sensitive 
     - If you use 'NaMe' in the command then in the Datasheet it will search for 'NaMe' 

### 2. Commands file
  - This file includes all the commands which you want to generate.
  - Use the following syntax:
    - cmd_id \[separator\] command 
    - example: 
       * start_host : start_host -name [Hostname] -time [Time]
         - start_host is the cmd_id so it will search as the command to generate
         - ':' is the \[separator\] which separates the cmd_id and the command string
  
## Help message
If you miss something command-fuse will help you with an error message.
In the message it will be specified the error type and the message.

## Default values for Command-Fuse
 ### 1. Commands file
  - .txt file for input
  - separator is **':'**
  - left column parenthesis is **'\['**
  - right column parenthesis is **'\]'**
  
 ### 2. Datasheet file:
  - command column is **'CMD'**
  - commands separator is **';'**
  - extension is mandatory
