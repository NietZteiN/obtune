import std.math;
import std.typecons;
import std.array;

long[] f(long[] array, long index, long value) {
    array.insertInPlace(0, index + 1);
    if (value >= 1) {
        array.insertInPlace(index, value);
    }
    return array;
}

unittest
{
    alias candidate = f;

    assert(candidate([2L], 0L, 2L) == [2L, 1L, 2L]);
}
void main(){}
