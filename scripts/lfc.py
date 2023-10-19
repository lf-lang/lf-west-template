
from west.commands import WestCommand  # your extension must subclass this
from west import log                   # use this for user output

import os
import shutil
import subprocess

class Lfc(WestCommand):
    def __init__(self):
        super().__init__(
            'lfc',               # gets stored as self.name
            'A wrapper around the Lingua Franca Compiler (lfc)',  # self.help
            ""
        )
        # To use a specific lfc binary the following variable can be modified
        # or the path to the desired binary can be passed to `--lfc`
        self.lfcPath = "lfc"

    def do_add_parser(self, parser_adder):
        parser = parser_adder.add_parser(self.name,
                                         help=self.help,
                                         description=self.description)

        parser.add_argument('app', help='Name of main LF file')
        parser.add_argument('--build', nargs='?', const=" ", help='Invoke `west build` after code-generation')
        parser.add_argument('--lfc', help='Path to LFC binary')

        return parser           # gets stored as self.parser

    def do_run(self, args, unknown_args):
        
        # Verify that the project is laid out correctly
        if "src" not in args.app.split("/"):
            print("ERROR: West lfc must be invoked outside `src` folder")

        # Your input file path
        # file_path = "/path/to/old_directory/filename.txt"

        # Remove the file extension
        # file_name, file_extension = os.path.splitext(file_path)
        # file_name = os.path.basename(file_name)

        # Replace the directory name
        # new_directory_name = "new_directory"
        # file_path = file_path.replace("old_directory", new_directory_name)

        # Combine the modified path with the new directory name
        # new_path = os.path.join(os.path.dirname(file_path), file_name + file_extension)

        # print(new_path)

        # Find the path where lfc will put the generated sources
        srcGenPath = args.app.split(".")[0].replace("src", "src-gen")
        appPath = args.app.split("src")[0]
        if appPath == "":
            appPath = "."

        if args.lfc:
            self.lfcPath = args.lfc
        
        # 1. Invoke lfc
        lfcCmd = f"{self.lfcPath} -c -n {args.app}"
        print(f"Executing lfc command: `{lfcCmd}`")
        res = subprocess.Popen(lfcCmd, shell=True)
        ret = res.wait()
        if ret != 0:
            exit(1)
        
        # 2. Copy prj.conf and Kconfig into the src-gen folder
        shutil.copyfile(f"{appPath}/Kconfig", f"{srcGenPath}/Kconfig")
        shutil.copyfile(f"{appPath}/prj.conf", f"{srcGenPath}/prj.conf")
        
        # Invoke west in the `src-gen` directory. Pass in 
        if args.build:
          westCmd = f"west build {srcGenPath} {args.build}"
          print(f"Executing west command: `{westCmd}`")
          res = subprocess.Popen(westCmd, shell=True)
          ret = res.wait()
          if ret != 0:
              exit(1)