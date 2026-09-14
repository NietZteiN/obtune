import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] lst) 
{
    if (lst.length > 4)
        lst[1..4].reverse();
    else if (lst.length > 1)
        lst[1..$].reverse();
    return lst;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L]) == [1L, 3L, 2L]);
}
void main(){}
