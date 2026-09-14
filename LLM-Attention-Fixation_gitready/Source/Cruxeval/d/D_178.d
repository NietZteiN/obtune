import std.math;
import std.typecons;
long[] f(long[] array, long n) 
{
    return array[n..$];
}
unittest
{
    alias candidate = f;

    assert(candidate([0L, 0L, 1L, 2L, 2L, 2L, 2L], 4L) == [2L, 2L, 2L]);
}
void main(){}
