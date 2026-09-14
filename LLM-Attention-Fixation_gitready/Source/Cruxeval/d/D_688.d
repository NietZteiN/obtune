import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] nums) 
{
    long[] l;
    foreach (i; nums)
    {
        if (!l.canFind(i))
        {
            l ~= i;
        }
    }
    return l;
}
unittest
{
    alias candidate = f;

    assert(candidate([3L, 1L, 9L, 0L, 2L, 0L, 8L]) == [3L, 1L, 9L, 0L, 2L, 8L]);
}
void main(){}
