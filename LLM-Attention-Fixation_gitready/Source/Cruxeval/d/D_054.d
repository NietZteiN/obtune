import std.math;
import std.typecons;
import std.string;
import std.algorithm;

long f(string text, long s, long e) 
{
    string sublist = text[s .. e];
    if (sublist.empty)
    {
        return -1;
    }
    return sublist.indexOf(minElement(sublist));
}
unittest
{
    alias candidate = f;

    assert(candidate("happy", 0L, 3L) == 1L);
}
void main(){}
