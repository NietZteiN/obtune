import std.math;
import std.typecons;
import std.array;

long[] f(long[] array) 
{
    if (array.length > 0) {
        auto n = array.back;
        array.length--;
        array ~= n;
        array ~= n;
    }
    return array;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 1L, 2L, 2L]) == [1L, 1L, 2L, 2L, 2L]);
}
void main(){}
