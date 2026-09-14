import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] array) 
{
    auto result = array.dup;
    result = result.reverse.array;
    foreach(ref item; result)
    {
        item *= 2;
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L, 4L, 5L]) == [10L, 8L, 6L, 4L, 2L]);
}
void main(){}
