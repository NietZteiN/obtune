import std.math;
import std.typecons;
import std.algorithm;

long[] f(long[] m) 
{
    m.reverse();
    return m;
}
unittest
{
    alias candidate = f;

    assert(candidate([-4L, 6L, 0L, 4L, -7L, 2L, -1L]) == [-1L, 2L, -7L, 4L, 0L, 6L, -4L]);
}
void main(){}
