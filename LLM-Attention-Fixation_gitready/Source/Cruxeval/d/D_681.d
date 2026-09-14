import std.math;
import std.typecons;

long[] f(long[] array, long ind, long elem)
{
    ind = ind < 0 ? -5 : (ind > array.length ? array.length : ind + 1);
    array = array[0 .. ind] ~ [elem] ~ array[ind .. $];
    return array;
}

unittest
{
    alias candidate = f;

    assert(candidate([1L, 5L, 8L, 2L, 0L, 3L], 2L, 7L) == [1L, 5L, 8L, 7L, 2L, 0L, 3L]);
}
void main(){}
