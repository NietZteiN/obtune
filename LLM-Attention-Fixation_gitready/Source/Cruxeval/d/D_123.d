import std.typecons;
import std.array;

long[] f(long[] array, long elem)
{
    foreach (idx, e; array)
    {
        if (e > elem && array[idx - 1] < elem)
        {
            array = array[0 .. idx] ~ [elem] ~ array[idx .. $];
            break;
        }
    }
    return array;
}

unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L, 5L, 8L], 6L) == [1L, 2L, 3L, 5L, 6L, 8L]);
}
void main(){}
