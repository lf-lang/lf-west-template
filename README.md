# Lingua Franca West Template
This is a west-centric project template for Lingua Franca applications targeting the Zephyr RTOS.
To use this template do the following steps:


## Getting started

1. Install Zephyr SDK and toolchain as described [here](https://docs.zephyrproject.org/3.7.0/develop/getting_started/index.html#install-the-zephyr-sdk)

2. Setup a virtual environment with west installed
```
python3 -m venv .venv
source .venv/bin.activate
pip install west
```

3. Pull down the Zephyr RTOS sources into `deps/zephyr`
```
west update
west zephyr-export
pip install -r deps/zephyr/scripts/requirements.txt
```

## Try an example app
```
cd apps/HelloWorld
west lfc --build
west build -t run
```