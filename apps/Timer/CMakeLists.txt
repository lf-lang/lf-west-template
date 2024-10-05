cmake_minimum_required(VERSION 3.20.0)
set(PLATFORM "ZEPHYR" CACHE STRING "Platform to target")
set(BOARD nrf52dk_nrf52832)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(reactor-uc-zephyr)

add_subdirectory(src-gen/Timer)

target_sources(app PRIVATE main.c)
target_link_libraries(app PRIVATE Timer)