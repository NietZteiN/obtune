import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.conv;

long countOccurrences(string[] arr, string element)
{
    return count(arr, element);
}

long[] f(string[] li) 
{
    long[] result;
    foreach (i; li) {
        result ~= countOccurrences(li, i);
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate(["k", "x", "c", "x", "x", "b", "l", "f", "r", "n", "g"]) == [1L, 3L, 1L, 3L, 3L, 1L, 1L, 1L, 1L, 1L, 1L]);
}
void main(){}
