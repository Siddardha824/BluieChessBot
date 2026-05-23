#include "tools/Tests.hpp"
#include <iostream>

int main()
{
    std::cout << "Starting BluieChessBot Correctness Verification Tests...\n";
    testMagicAttacks();
    std::cout << "All verification tests completed.\n";
    return 0;
}