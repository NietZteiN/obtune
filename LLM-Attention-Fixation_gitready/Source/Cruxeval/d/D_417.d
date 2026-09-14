import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] lst) 
{
    lst = lst.dup.reverse;
    lst = lst[0 .. $-1];
    return lst.dup.reverse;
}
unittest
{
    alias candidate = f;

    assert(candidate([7L, 8L, 2L, 8L]) == [8L, 2L, 8L]);
}
void main(){}
