import std.math;
import std.typecons;
import std.array;
import std.algorithm;

long[] f(long[] array, long num) 
{
    bool reverse = false;
    if (num < 0) {
        reverse = true;
        num *= -1;
    }
    array.reverse();
    long[] result = new long[array.length * num];
    foreach (immutable i; 0 .. num) {
        result[i * array.length .. (i+1) * array.length] = array;
    }
    if (reverse) {
        result.reverse();
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L], 1L) == [2L, 1L]);
}
void main(){}
