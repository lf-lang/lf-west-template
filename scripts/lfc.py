
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
        parser.add_argument('--board', help='Board selection, which is passed to `west build` if invoked')
        parser.add_argument('--lfc', help='Path to LFC binary')

        return parser           # gets stored as self.parser

    def do_run(self, args, unknown_args):
        
        if args.build and not args.board:
            print("ERROR: build option selected but no board was passed")
            exit(1)
        
        # Verify that the project is laid out correctly
        if "src" not in args.app:
            print("ERROR: LF app must be inside a `src` folder")
            exit(1)


        # Find the path to where lfc will put the sources
        appPath, app_ext = os.path.splitext(args.app)
        appName = os.path.basename(appPath)
        srcGenPath = appPath.replace("src", "src-gen")
        rootPath = appPath.split("src")[0]

        if args.lfc:
            self.lfcPath = args.lfc
        
        # 1. Invoke lfc
        lfcCmd = f"{self.lfcPath} -c -n {args.app}"
        print(f"Executing lfc command: `{lfcCmd}`")
        res = subprocess.Popen(lfcCmd, shell=True)
        ret = res.wait()
        if ret != 0:
            exit(1)
        
        # 2. Copy prj.conf, Kconfig and app.overlay into the src-gen folder
        for f in ("Kconfig", "prj.conf", "app.overlay"):
            src = os.path.join(rootPath, f)
            dst = os.path.join(srcGenPath, f)
            if not os.path.exists(src):
                print(f"Did not find {f} at {src}. Project layout is incorrect")
                exit(1)
            shutil.copyfile(src, dst)
        
        # 3. Add board/<board>.overlay and app.overlay to the DTC_OVERLAY_FILE
        # variable, so west picks them both up
        #
        # Note: The ordering here matters 
        # (see https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/zephyr/build/dts/howtos.html#set-devicetree-overlays)
        cmake_args = f"-DDTC_OVERLAY_FILE=\"app.overlay boards/{args.board}.overlay\""
        
        # Invoke west in the `src-gen` directory. Pass in 
        if args.build:
          westCmd = f"west build {srcGenPath} {args.build} -b {args.board} -- {cmake_args}"
          print(f"Executing west command: `{westCmd}`")
          res = subprocess.Popen(westCmd, shell=True)
          ret = res.wait()
          if ret != 0:
              exit(1)