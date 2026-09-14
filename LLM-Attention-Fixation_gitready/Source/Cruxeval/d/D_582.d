import std.math;
import std.typecons;
long[] f(long k, long j) 
{
    long[] arr;
    foreach (i; 0 .. k) {
        arr ~= j;
    }
    return arr;
}
unittest
{
    alias candidate = f;

    assert(candidate(7L, 5L) == [5L, 5L, 5L, 5L, 5L, 5L, 5L]);
}
void main(){}
