
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
        self.lfcPath = "/home/erling/dev/reactor-uc/lfc/bin/lfc-dev"
        self.lfSrcPath = "src"

    def do_add_parser(self, parser_adder):
        parser = parser_adder.add_parser(self.name,
                                         help=self.help,
                                         description=self.description)

        parser.add_argument('--lfc', help='Path to LFC binary')
        parser.add_argument('-b', '--build', help='Invoke west build after', action='store_true')

        return parser           # gets stored as self.parser

    def run_cmd(self, cmd):
        print(f"Executing command: `{cmd}`")
        res = subprocess.Popen(cmd, shell=True)
        ret = res.wait()
        if ret != 0:
            exit(1)


    def run_lfc(self, file_path):
        lfcCmd = f"{self.lfcPath} -n {file_path}"
        self.run_cmd(lfcCmd)


    def run_west_build(self):
        westCmd = "west build -p always"
        self.run_cmd(westCmd)


    def do_run(self, args, unknown_args):
        if args.lfc:
            self.lfcPath = args.lfc
        
        foundFile = False
        
        # 1. Invoke lfc on all source files in folder containing a main reactor
        for filename in os.listdir(self.lfSrcPath):
            # Construct the full file path
            file_path = os.path.join(self.lfSrcPath, filename)

            # Check if it's a file (not a directory)
            if os.path.isfile(file_path):
                # Example: open the file and read its content
                with open(file_path, 'r') as file:
                    content = file.read()
                    if content.find("main reactor"):
                        self.run_lfc(file_path)
                        foundFile = True
        if foundFile:
            if args.build:
                self.run_west_build()
        else:
            print(f"Did not find any LF files with main reactor in {self.lfSrcPath}")
            exit(1) 
