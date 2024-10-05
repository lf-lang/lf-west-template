cmake_minimum_required(VERSION 3.20.0)
set(PLATFORM "ZEPHYR" CACHE STRING "Platform to target")
set(BOARD qemu_cortex_m3)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(reactor-uc-zephyr)

add_subdirectory(src-gen/HelloWorld)

target_sources(app PRIVATE main.c)
target_link_libraries(app PRIVATE HelloWorld)