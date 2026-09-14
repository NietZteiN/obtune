import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] lst) 
{
    long[] new_list = lst.dup;
    new_list.sort();
    return lst;
}
unittest
{
    alias candidate = f;

    assert(candidate([6L, 4L, 2L, 8L, 15L]) == [6L, 4L, 2L, 8L, 15L]);
}
void main(){}
