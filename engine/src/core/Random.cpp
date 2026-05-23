#include "core/Random.hpp"
#include "core/Types.hpp"
#include <cstdint>

// pseudo random number state
uint32_t randomState = 1804289383;

// generate 32-bit pseudo legal numbers
uint32_t getRandomU32Number()
{
    // get current state
    uint32_t number = randomState;

    // XOR shift algorithm
    number ^= number << 13;
    number ^= number >> 17;
    number ^= number << 5;

    // update random number state
    randomState = number;

    // return random number
    return number;
}

// generate 64-bit pseudo legal numbers
Bitboard getRandomBitboardNumber()
{
    // define 4 random numbers
    Bitboard n1, n2, n3, n4;

    // init random numbers slicing 16 bits from MS1B side
    n1 = (Bitboard)(getRandomU32Number()) & 0xFFFF;
    n2 = (Bitboard)(getRandomU32Number()) & 0xFFFF;
    n3 = (Bitboard)(getRandomU32Number()) & 0xFFFF;
    n4 = (Bitboard)(getRandomU32Number()) & 0xFFFF;

    // return random number
    return n1 | (n2 << 16) | (n3 << 32) | (n4 << 48);
}

// generate magic number candidate
Bitboard generateMagicNumber()
{
    return getRandomBitboardNumber() & getRandomBitboardNumber() & getRandomBitboardNumber();
}