import std.math;
import std.typecons;
import std.range;
import std.algorithm;
import std.typecons;

long[][] f(long n, long[] array) 
{
    long[][] final_;
    final_ ~= array.dup;
    foreach (immutable _; 0 .. n)
    {
        long[] arr = array.dup;
        arr ~= final_.back;
        final_ ~= arr;
    }
    return final_;
}
unittest
{
    alias candidate = f;

    assert(candidate(1L, [1L, 2L, 3L]) == [[1L, 2L, 3L], [1L, 2L, 3L, 1L, 2L, 3L]]);
}
void main(){}
