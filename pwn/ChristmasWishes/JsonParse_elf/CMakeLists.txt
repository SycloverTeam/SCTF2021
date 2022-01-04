cmake_minimum_required(VERSION 3.20)
project(JsonParse C)

set(CMAKE_C_STANDARD 11)
add_compile_options(-Wall -no-pie -O0)
add_link_options(-no-pie)

include_directories(.)

set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)
add_executable(JsonParser main.c JsonParser.c)

