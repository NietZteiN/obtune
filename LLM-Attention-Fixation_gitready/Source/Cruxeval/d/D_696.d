import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.range;

long f(string text) 
{
    long s = 0;
    foreach (i; 1 .. text.length)
    {
        auto parts = text.splitter(text[i]);
        s += parts.front.length;
    }
    return s;
}
unittest
{
    alias candidate = f;

    assert(candidate("wdj") == 3L);
}
void main(){}
