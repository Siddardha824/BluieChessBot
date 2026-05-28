#pragma once

/**
 * @file Attacks.hpp
 * @brief Centralized unified runtime entry point for the BluieChessBot attack systems.
 *
 * Provides access to both leaper piece attacks (pawns, knights, kings) and
 * sliding piece attacks (bishops, rooks, queens) through a single inclusion.
 */

#include "attacks/LeaperAttacks.hpp" // IWYU pragma: keep
#include "attacks/MagicIndexing.hpp" // IWYU pragma: keep