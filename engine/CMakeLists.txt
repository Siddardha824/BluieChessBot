cmake_minimum_required(VERSION 3.16)

project(BluieChessBot)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include_directories(include)

add_executable(BluieChessBot
    src/Bluie.cpp
    src/core/Debug.cpp
    src/core/Random.cpp
    src/attacks/Attacks.cpp
    src/attacks/MagicNumbers.cpp
    src/board/Board.cpp
    src/tools/Tests.cpp
)