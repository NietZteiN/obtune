import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] array, long L) 
{
    if (L <= 0)
        return array;
    if (array.length < L) 
    {
        array ~= array.replicate(L - array.length);
    }
    return array;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L], 4L) == [1L, 2L, 3L, 1L, 2L, 3L]);
}
void main(){}
