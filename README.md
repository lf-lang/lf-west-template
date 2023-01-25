# Lingua Franca Zephyr Template

This repository contains a template for Lingua Franca applications using the
Zephyr target platform. It contains a `west` extensions which takes care of
invoking `lfc`.

## Requirements
- Linux system (or WSL). Should be fine on macos also, but not tested yet.
- An installation of `lfc` which is more recent than commit `788ba74` where
  zephyr support was added
- Zephyr development environment, please check out v3.2.0. See [Zephyr Getting Started Guide](https://docs.zephyrproject.org/latest/getting_started/index.html).

### Initialization
If you followed the [Zephyr Getting Started
Guide](https://docs.zephyrproject.org/latest/getting_started/index.html). You
will have installed the following:
1. west build tool
2. Zephyr SDK
3. Zephyr source code

#### (Optional) Install Zephyr environment locally in this repository
The Zephyr source code can also be installed locally in this repository. By
running:
```
west init && west update
```

### Build & Run

#### QEMU emulation
```
west lf-build src/HelloWorld.lf -w "-t run"
```

#### Nrf52 blinky
```
west lf-build src/NrfBlinky.lf -w "-b nrf52dk_nrf52832"
west flash
```

The custom `lf-build` west command can be inspected in `scripts/lf_build.py`. It
invokes `lfc` on the provided LF source file. It then invokes `west build` on
the generated sources. `west lf-build -h` # lf-zephyr-template
