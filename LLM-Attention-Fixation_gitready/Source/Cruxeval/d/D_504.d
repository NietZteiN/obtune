import std.math;
import std.typecons;
import std.algorithm;

long[] f(long[] values) 
{
    values.sort();
    return values;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 1L, 1L, 1L]) == [1L, 1L, 1L, 1L]);
}
void main(){}
