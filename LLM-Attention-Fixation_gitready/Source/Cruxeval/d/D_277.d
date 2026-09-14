import std.math;
import std.typecons;
import std.algorithm;

long[] f(long[] lst, long mode) 
{
    long[] result = lst.dup;
    if (mode != 0) {
        result = result.reverse;
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L, 4L], 1L) == [4L, 3L, 2L, 1L]);
}
void main(){}
