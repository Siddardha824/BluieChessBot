#include "uci/UCI.hpp"
#include <iostream>

int main()
{
    try
    {
        Bluie::UCI uci;
        uci.loop();
    }
    catch (const std::exception& e)
    {
        std::cerr << "Fatal Engine Error: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}