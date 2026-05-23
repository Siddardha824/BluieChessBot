cmake_minimum_required(VERSION 3.16)

project(BluieChessBot)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include_directories(include)

add_executable(BluieChessBot
    src/Bluie.cpp
    src/Debug.cpp
    src/Attacks.cpp
    src/MagicNumbers.cpp
    src/Board.cpp
    tools/Random.cpp
    tools/Tests.cpp
)