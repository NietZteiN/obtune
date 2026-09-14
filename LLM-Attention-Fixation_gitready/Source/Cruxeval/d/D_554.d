import std.math;
import std.typecons;
import std.algorithm;

long[] f(long[] arr) 
{
    return arr.dup.reverse;
}
unittest
{
    alias candidate = f;

    assert(candidate([2L, 0L, 1L, 9999L, 3L, -5L]) == [-5L, 3L, 9999L, 1L, 0L, 2L]);
}
void main(){}
