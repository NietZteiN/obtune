import std.math;
import std.typecons;
import std.algorithm: reverse;
import std.range: iota;

long[] f(long[] array) 
{
    auto new_array = array.dup;
    new_array.reverse();
    foreach (i, ref x; new_array)
        x = x*x;
    return new_array;
}

unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 1L]) == [1L, 4L, 1L]);
}
void main(){}
