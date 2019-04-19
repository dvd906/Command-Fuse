import argparse
import os
import sys
import time

import modules.command_parser      as command_parser
import modules.data_parser         as data_parser
import modules.cmd_fuse_exception  as cmd_fuse_exception 
import modules.cmd_deployer        as cmd_deployer

_CURRENT_PATH = os.path.dirname(__file__) + os.sep
_PACKAGE_PATH = _CURRENT_PATH + 'packages' + os.sep
_SAVE_PATH = _CURRENT_PATH + 'fused_commands' + os.sep

_GROUP_INPUT = {
    'seq' : cmd_deployer.CommandSeparationType.sequential,
    'group' : cmd_deployer.CommandSeparationType.group
    }
_PACKAGE_GENERATE_SLEEP_TIME = 1

_HELP_VIEW = "<< CMD_FUSE v1.0 >>\n\
-- to generate command --\n\
  -f [data path] -d [commands_path] \n\
  or \n\
  -f [data_path] -d [package_name] \n\
   in this case the package needs to exist \n\n\
-- to add package --\n\
  -f [commands_path] -a [package_name] \n\
"

def create_dir_if_not_exist(path):
    if not os.path.exists(path):
        os.mkdir(path)

def create_parser():
    user_values = list(_GROUP_INPUT.keys())
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, help='Current path for the commands or data')
    parser.add_argument('-d', '--deploy', type=str, help='Path for commands or a package name to generate from')
    parser.add_argument('-a', '--add_package', type=str, help='If -f used then you need to add a name for the package')
    parser.add_argument('-g', '--group', 
                        type=str, help='Separates the command {}'.format(user_values),
                        default=cmd_deployer.CommandSeparationType.sequential)
    parser.add_argument('-not_print', '--not_print', action="store_true", 
                        help='The output shows on screen')

    parser.add_argument('-save', '--is_save_to_deployed', action="store_true",
                        help='Save it to file current path {} if no save path provided'.format(_SAVE_PATH))
    parser.add_argument('-sp', '--save_path', help='The fuesd commands to save',
                        default=_SAVE_PATH)

    parser.add_argument('-csep', '--command_separator',
                        type=str, help='The [separator] value for [commands] file',
                        default=command_parser.CommandPackage.BASE_SEPARATOR)
    parser.add_argument('-dsep', '--data_command_sep', 
                        type=str, help='The [separator] value for [data] file',
                        default=cmd_deployer.CommandFuse.BASE_COMMAND_SEP)
    parser.add_argument('-col', '--command_column', type=str,
                        help='The command column from the data file',
                        default=cmd_deployer.CommandFuse.BASE_COMMAND_COLUMN)
    
    parser.add_argument('-col_sub_left', type=str, 
                        help='The column name left side character',
                        default=command_parser.CommandPackage.COL_SUB_LEFT)
    parser.add_argument('-col_sub_right', type=str,
                        help='The column name right side character',
                        default=command_parser.CommandPackage.COL_SUB_RIGHT)
    parser.add_argument('-col_to_replace', type=str, 
                        help='The column characters to substitute',
                        default=command_parser.CommandPackage.TO_REPLACE)
    parser.add_argument('-show', '--show_avialable', action="store_true",
                        help='Shows the avialable packages')

    return parser

def main():
    create_dir_if_not_exist(_PACKAGE_PATH)
    create_dir_if_not_exist(_SAVE_PATH)

    parser = create_parser()
    can_show_usage = ['-h', '--help'] in sys.argv or len(sys.argv) == 1
    if can_show_usage:
        print(_HELP_VIEW)
    args = parser.parse_args()

    if args.show_avialable:
        print('Avialable packages')
        packages = os.listdir(_PACKAGE_PATH)
        for package in packages:
            print(package)

    if args.file and args.deploy:
        commands = None
        package_name = args.deploy

        if os.path.isfile(args.deploy):
            commands_file_path = args.deploy
            package_name = args.deploy.split(os.sep)[-1]
            if '.' in package_name:
                package_name = package_name.split('.')[0]
  
            cmd_package = command_parser.CommandPackage(
                commands_file_path, package_name, args.command_separator)
            cmd_package.deploy_package(_PACKAGE_PATH)

            print("Package \'{}\' generated".format(package_name))

            time.sleep(_PACKAGE_GENERATE_SLEEP_TIME)

        data = data_parser.RawDataParser(args.file).data
        package_path = _PACKAGE_PATH + package_name

        commands_from_package = command_parser.CommandPackage().load_package(package_path)

        deployer = cmd_deployer.CommandFuse(
            data, commands_from_package, args.command_column, 
            args.data_command_sep, args.group
        )
        if args.is_save_to_deployed:
            path = args.save_path
            if args.save_path == _SAVE_PATH:
                path = path + package_name
            deployer.fuse_to_file(path)
        generated_commands = deployer.fuse()

        if not args.not_print:
            for cmd in generated_commands:
                print(cmd)

        print('Commands generated')

    if args.file and args.add_package:
        cmd_package = command_parser.CommandPackage(args.file, args.add_package)
        cmd_package.deploy_package(_PACKAGE_PATH)
        
        print('Package saved')

if __name__ == '__main__':
    try:
        main()
    except cmd_fuse_exception.CommandFuseError as fuse_run_error:
        print('Error at fuse process:')
        print(fuse_run_error)
    except FileNotFoundError as file_not_found:
        print(file_not_found)