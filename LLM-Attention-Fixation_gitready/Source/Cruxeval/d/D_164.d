import std.math;
import std.typecons;
import std.algorithm;

long[] f(long[] lst) 
{
    lst.sort();
    return lst[0..3];
}
unittest
{
    alias candidate = f;

    assert(candidate([5L, 8L, 1L, 3L, 0L]) == [0L, 1L, 3L]);
}
void main(){}
