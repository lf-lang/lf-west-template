# Lingua Franca West Template

This repository contains a template for Lingua Franca applications using the
Zephyr target platform. It contains a `west` extension which takes care of
invoking `lfc`.

## Requirements
- Linux system (or WSL). Should be fine on MacOS also, but not tested yet.
- An installation of `lfc` which is more recent than commit `788ba74` where
  zephyr support was added. The nightly release can be downloaded [here](https://github.com/lf-lang/lingua-franca/releases). This version of `lfc` must the first `lfc` on the system path. Alternatively you can edit [this](https://github.com/lf-lang/lf-west-template/blob/main/scripts/lf_build.py#L15) line to give the path to the new lfc.

NB: This is a temporary workaround until v0.4 is released
  
  
  
## Zephyr
- In order to use this template the following Zephyr dependencies are needed:
1. West meta build tool (see [West information](https://docs.zephyrproject.org/latest/develop/west/index.html))
2. Zephyr SDK and toolchains

Please refer to [Zephyr Getting Started Guide](https://docs.zephyrproject.org/latest/getting_started/index.html). NB. You can skip steps 5,6,7 which clones the entire Zephyr project. Instead we will clone Zephyr into this workspace using west.

If `west` is installed in a virtual environment, this environment is assumed activated for the rest of this guide.

### Initialization
1. Clone this template and remove old git history:

```
$ git clone https://github.com/lf-lang/lf-zephyr-template/ lf-zephyr-app
$ cd lf-zephyr-app
```

2. Clone the Zephyr project into `deps/zephyr`:

```
$ west update
```

3. Install Zephyr python dependencies:

```
$ pip3 install -r deps/zephyr/scripts/requirements.txt
```

### Build & Run

#### QEMU emulation
```
$ cd application/HelloWorld
$ west lf-build src/HelloWorld.lf -w "-t run"
```

#### Blinky example

To run the blinky example on Nrf52 requires that the `nrfjprog` utility is installed. See installation guide [here](https://www.nordicsemi.com/Products/Development-tools/nrf-command-line-tools/download)

```
$ cd application/Blinky
$ west lf-build src/Blinky.lf -w "-b nrf52dk_nrf52832 -p always"
$ west flash
```

The custom `lf-build` west command can be inspected in `scripts/lf_build.py`. It
invokes `lfc` on the provided LF source file. It then invokes `west build` on
the generated sources. See `west lf-build -h` for more information.


## Federated Execution
Experimental federated execution is available for the Zephyr platform, tested with the board mimxrt1170_evk_cm7.

### Network Setup
To connect the sockets of an external federate (running on MCUs) and the RTI (running on the linux machine) both Zephyr configuration and network interface configuration with linux is necessary. The ethernet interface connecting the physical units must be initialized with an IP addresses on both ends.

#### Linux-side Setup
Check all network interface addresses on the linux machine by running 

```
$ ip address
```

The relevant ethernet interface should start with an 'e'. If several possible interfaces appear, then it is possible to check further hardware information (like connection info) on the suspected interface with the command 

```
$ sudo dmesg | grep -i <ETHERNET_INTERFACE_NAME>
```

This should make it possible to differentiate different ethernet interfaces. The linux machine side can then be assigned an address (in this example: 192.0.2.2) as follows

```
$ sudo ip address add dev <ETHERNET_INTERFACE_NAME> 192.0.2.2
```

To verify the interface address, check the interface addresses again. This address must match the IP address supplied in the federated LF code, ie. the RTI address specified in the code as

```
federated reactor at 192.0.2.2 {...}
```

Then, add an entry to the routing table with gateway and netmask information, with the following command. This is needed in order to correctly route the data traffic.

```
$ sudo ip route add 192.0.2.0/24 dev <ETHERNET_INTERFACE_NAME>
```

The routing table entries can be checked with

```
$ ip route
```

Take special note that these changes are not necessarily persistent, and will be lost with a restart, unless the commands are added to the user's script file or the linux distributions configuration files.

#### Board-side Setup
On the federate application side, networking and the POSIX API must be enabled and configured with Zephyr configuration options in the file `prj_<FED_NAME>.conf`. The following is a base configuration file to work from, and is provided in the federated program examples. In this example, the federate is assigned the IP address 192.0.2.1.

```
# General config
CONFIG_MAIN_STACK_SIZE=4096
CONFIG_TEST_RANDOM_GENERATOR=y
CONFIG_INIT_STACKS=y
CONFIG_POSIX_API=y
CONFIG_POSIX_MAX_FDS=32

# Generic networking options
CONFIG_NETWORKING=y
CONFIG_NET_UDP=y
CONFIG_NET_TCP=y
CONFIG_NET_IPV4=y
CONFIG_NET_SOCKETS=y
CONFIG_NET_L2_ETHERNET=y
CONFIG_NET_MAX_CONN=32
CONFIG_NET_MAX_CONTEXTS=32

# Network buffers
CONFIG_NET_PKT_RX_COUNT=32
CONFIG_NET_PKT_TX_COUNT=32
CONFIG_NET_BUF_RX_COUNT=128
CONFIG_NET_BUF_TX_COUNT=128
CONFIG_NET_BUF_FIXED_DATA_SIZE=y
CONFIG_NET_BUF_DATA_SIZE=1024

# Network socket timeout
CONFIG_NET_CONTEXT_RCVTIMEO=y
CONFIG_NET_CONTEXT_SNDTIMEO=y

# Network application options and configuration
CONFIG_NET_CONFIG_SETTINGS=y
CONFIG_NET_CONFIG_NEED_IPV4=y
CONFIG_NET_CONFIG_MY_IPV4_ADDR="192.0.2.1"
CONFIG_NET_CONFIG_MY_IPV4_GW="192.0.2.0"
CONFIG_NET_CONFIG_MY_IPV4_NETMASK="255.255.255.0"
```

Additionally, it can be useful for debugging purposes to add the Zephyr network shell functionality. This makes it possible to use the serial communication client as input for some select commands, for example, to print network configuration info from the board. Also setting the option the receive network debugging info is useful. These options are available by including `debug.conf` when building the application.

```
# Network Shell
CONFIG_NET_SHELL=y
CONFIG_SHELL=y

# Debug info
CONFIG_NET_LOG=y
CONFIG_LOG=y
CONFIG_NET_STATISTICS=y
CONFIG_NET_SOCKETS_LOG_LEVEL_DBG=y
```

Furthermore, the MAC addresses of the boards can be configured using DTS overlay files (`<BOARD_NAME>_<FED_NAME>.overlay`). This is important to be aware of as the boards might get the same MAC address by default. Overlay-files that do this are provided in the example federated programs. The MAC address is set with

```
&enet {
	local-mac-address = [00 0a 35 00 00 01];
	status = "okay";
};
```

Other application-specific hardware configurations can be added in this file.

### Build
To build a federated LF application, run

```
$ cd application/<APPLICATION_NAME>
$ west lf-fed-build src/<APPLICATION_NAME>.lf -w "-b mimxrt1170_evk_cm7 --pristine"
```

This command will generate a build folder per federate with name "zephyr-<FED_NAME>-build".

It is possible to specify federates to build by adding

```
$ west lf-fed-build src/<APPLICATION_NAME>.lf -w "-b mimxrt1170_evk_cm7 --pristine" -f <FED_NAME1> <FED_NAME2>
```

To build with debugging configurations in `debug.conf` run

```
$ west lf-fed-build src/<APPLICATION_NAME>.lf -w "-b mimxrt1170_evk_cm7 --pristine" -c debug.conf
```

To build without running the `lfc` command can be useful if modifying the auto-generated code. This can be done by passing the command-line option `-n` to the lf-fed-build command.

The lf-fed-build can be inspected in `scripts/lf_build.py`. By default, it invokes `lfc` on the provided LF source file. It then copies over necessary Zephyr configuration files to each generated federate. Then `west build` is invoked on each federate, resulting in a build folder per federate.

### Flash

To flash n federates to at least n connected boards, a custom west command called `lf-fed-flash` is supplied. The only command-line option is `-n` which accepts an integer representing the number of federates to flash. It must match the number of build folders in the current directory (where the command is called from). 

For example, if three boards are connected and three federates should be flashed, run

```
$ west lf-fed-flash -n 3
```
To use this command, it is necessary that debugging is set up properly, and specifically using the `pyocd` runner. 

### Debugger Setup
Test debugging with `pyocd` by building and flashing a basic Zephyr sample
```
$ cd deps/zephyr/samples/hello_world
$ west build src/main.c
$ west flash -r pyocd
```
PyOCD is the preferred runner since it is compatible with the out-of-the-box firmware on NXP MIMXRT1170-EVK, which is CMSIS-DAP. It is also possible to use JLink tools, but then the firmware must be changed.

If the following error occurs
```
[Errno 13] Access denied (insufficient permissions) while trying to interrogate a USB device. This can probably be remedied with a udev rule. See <https://github.com/pyocd/pyOCD/tree/master/udev> for help.
```
Then a udev rule must be set up, as indicated by the error itself. To add a udev rule, do the following
```
$ cd /etc/udev/rules.d
$ sudo touch 50-cmsis-dap.rules
```
Then, copy the contents from the file `https://github.com/pyocd/pyOCD/blob/main/udev/50-cmsis-dap.rules` into the newly created file. Reload the new rules by
```
$ sudo udevadm control --reload
$ sudo udevadm trigger
```

It should then be possible to run the `west flash -r pyocd` command.

If PyOCD is setup, then debugging with GDB can be done by simply running

```
$ west debug -r pyocd
```

### Run

To run a federation, start the RTI with ID "Unidentified Federation" and supplying the number of federates to connect. This can be federates running from boards or also from a linux computer. For example, run

```
$ RTI -n 3 -i "Unidentified Federation"
```

Then each board federate must be restarted.
