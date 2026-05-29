cmake_minimum_required(VERSION 3.16)

project(BluieChessBot)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Find multithreading package for async search threads
find_package(Threads REQUIRED)

include_directories(include .)

add_executable(BluieChessBot
    src/Bluie.cpp
    src/core/Debug.cpp
    src/core/MoveGen.cpp
    src/core/Evaluation.cpp
    src/core/Search.cpp
    src/board/Board.cpp
    src/uci/UCI.cpp
    src/attacks/AttacksAPI.cpp
    tools/Random.cpp
    tools/AttacksOnTheFly.cpp
    tools/MagicGenerator.cpp
    tools/Tests.cpp
)

# Link platform-independent threads package
target_link_libraries(BluieChessBot PRIVATE Threads::Threads)