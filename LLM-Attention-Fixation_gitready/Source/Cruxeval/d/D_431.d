import std.math;
import std.typecons;
import std.range;
import std.array;

long[] f(long n, long m) 
{
    long[] arr = new long[](n);
    foreach (i; 0 .. n) {
        arr[i] = i + 1;
    }
    foreach (_; 0 .. m) {
        arr = [];
    }
    return arr;
}
unittest
{
    alias candidate = f;

    assert(candidate(1L, 3L) == []);
}
void main(){}
