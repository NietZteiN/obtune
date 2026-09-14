import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long f(string needle, string haystack) 
{
    long count = 0;
    while (haystack.canFind(needle))
    {
        haystack = haystack.replaceFirst(needle, "");
        count += 1;
    }
    return count;
}
unittest
{
    alias candidate = f;

    assert(candidate("a", "xxxaaxaaxx") == 4L);
}
void main(){}
