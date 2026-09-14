import std.math;
import std.typecons;
import std.algorithm.searching;
import std.algorithm.sorting;
import std.array;
import std.string;

long[] f(string text) 
{
    long[char] counts;
    auto txt = text.replace("-", "").toLower();
    foreach (c; txt)
    {
        if (c in counts)
            counts[c] += 1;
        else
            counts[c] = 1;
    }
    return counts.values.sort().array;
}
unittest
{
    alias candidate = f;

    assert(candidate("x--y-z-5-C") == [1L, 1L, 1L, 1L, 1L]);
}
void main(){}
