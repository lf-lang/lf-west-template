from west.commands import WestCommand  # your extension must subclass this
from west import log                   # use this for user output

import subprocess

class LfBuild(WestCommand):
    def __init__(self):
        super().__init__(
            'lf-build',               # gets stored as self.name
            'Compile LF program and then run west build',  # self.help
            ""
        )
        # To use a specific lfc binary the following variable can be modified
        # or the path to the desired binary can be passed to `--lfc`
        self.lfcPath = "lfc"

    def do_add_parser(self, parser_adder):
        # This is a bit of boilerplate, which allows you full control over the
        # type of argparse handling you want. The "parser_adder" argument is
        # the return value of an argparse.ArgumentParser.add_subparsers() call.
        parser = parser_adder.add_parser(self.name,
                                         help=self.help,
                                         description=self.description)

        # Add some example options using the standard argparse module API.
        # parser.add_argument('-o', '--optional', help='an optional argument')
        # parser.add_argument('project_root', help='Path to root of project')
        parser.add_argument('main_lf', help='Name of main LF file')
        parser.add_argument('-w', '--west-commands', help='Arguments to forward to west')
        parser.add_argument('-c', '--conf-overlays', help='Additional configuration overlays')
        parser.add_argument('--lfc', help='Path to LFC binary')

        return parser           # gets stored as self.parser

    def do_run(self, args, unknown_args):
        
        if "src" not in args.main_lf.split("/"):
            print("ERROR: West lf-build must be invoked outside `src` folder")

        srcGenPath = args.main_lf.split(".")[0].replace("src", "src-gen")
        appPath = args.main_lf.split("src")[0]
        if appPath == "":
            appPath = "."

        # 1. Invoke lfc with clean flag `-c` and without invoking target
        #    compiler `n`.
        if args.lfc:
            self.lfcPath = args.lfc
        
        lfcCmd = f"{self.lfcPath} -c -n {args.main_lf}"
        print(f"Executing lfc command: `{lfcCmd}`")
        res = subprocess.Popen(lfcCmd, shell=True)
        ret = res.wait()
        if ret != 0:
            exit(1)

        if not args.west_commands:
            args.west_commands = ""
        
        # FIXME: This is a not-intuitive limitation from the users prespective.
        # But we use `-DOVERLAY_CONFIG` to mix in the prj.conf from the app
        # directory with the prj_lf.conf in the `src-gen`
        if "-DOVERLAY_CONFIG" in args.west_commands:
            print("Error: Use `--conf-overlays` option to pass config overlays to west")

        # Copy project configurations into src-gen 
        userConfigPaths="prj.conf"
        res = subprocess.Popen(f"cp {appPath}/prj.conf {srcGenPath}/", shell=True)
        if args.conf_overlays:
            res = subprocess.Popen(f"cp {appPath}/{args.conf_overlays} {srcGenPath}/", shell=True)
            userConfigPaths += f";{args.conf_overlays}"

        # Copy the Kconfig file into the src-gen directory
        res = subprocess.Popen(f"cp {appPath}/Kconfig {srcGenPath}/", shell=True)
        ret = res.wait()
        if ret != 0:
            exit(1)
        
        # Parse the generated CompileDefinitions.txt which should be 
        # forwarded to west
        compileDefs = ""
        with open(f"{srcGenPath}/CompileDefinitions.txt") as f:
            for line in f:
                    line = line.replace("\n", "")
                    compileDefs += f"-D{line} "

        print(compileDefs)
        # Invoke west in the `src-gen` directory. Pass in 
        westCmd = f"west build {srcGenPath} {args.west_commands} -- -DOVERLAY_CONFIG=\"{userConfigPaths}\" {compileDefs}"
        print(f"Executing west command: `{westCmd}`")
        res = subprocess.Popen(westCmd, shell=True)
        ret = res.wait()
        if ret != 0:
            exit(1)