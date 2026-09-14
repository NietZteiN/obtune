import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.array;

long f(string s) 
{
    long count = 0;
    foreach (c; s)
    {
        if (s.count(c) > 1)
        {
            count++;
        }
    }
    return count;
}
unittest
{
    alias candidate = f;

    assert(candidate("abca dea ead") == 10L);
}
void main(){}
