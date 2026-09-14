import std.math;
import std.typecons;
import std.algorithm;
import std.array;

float[] f(long n) 
{
    auto values = [0: 3, 1: 4.5, 2: '-'];
    auto res = new float[0];
    foreach (i, j; values)
    {
        if (i % n != 2)
        {
            res ~= j;
        }
    }
    res.sort();
    return res;
}
unittest
{
    alias candidate = f;

    assert(candidate(12L) == [3L, 4.5]);
}
void main(){}
