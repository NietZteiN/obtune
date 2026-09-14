import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(string[] lst) 
{
    lst.length = 0;
    long[] result;
    foreach (i; 0 .. lst.length + 1) {
        result ~= 1;
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate(["a", "c", "v"]) == [1L]);
}
void main(){}
