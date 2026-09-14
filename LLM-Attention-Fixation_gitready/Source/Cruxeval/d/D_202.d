import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] array, long[] lst) {
    array ~= lst; // Extend array with lst
    // Return elements that are greater than or equal to 10
    return array.filter!(e => e >= 10).array;
}

unittest
{
    alias candidate = f;

    assert(candidate([2L, 15L], [15L, 1L]) == [15L, 15L]);
}
void main(){}
