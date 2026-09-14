import std.math;
import std.typecons;
import std.array;
import std.algorithm;

long[][] f(long[][] matr, long insert_loc) 
{
    matr = matr[0..insert_loc] ~ [[]] ~ matr[insert_loc..$];
    return matr;
}
unittest
{
    alias candidate = f;

    assert(candidate([[5L, 6L, 2L, 3L], [1L, 9L, 5L, 6L]], 0L) == [[], [5L, 6L, 2L, 3L], [1L, 9L, 5L, 6L]]);
}
void main(){}
