import std.math;
import std.typecons;
import std.algorithm;

long[] f(long[] numbers, long elem, long idx) 
{
    numbers ~= elem;
    return numbers;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L], 8L, 5L) == [1L, 2L, 3L, 8L]);
}
void main(){}
