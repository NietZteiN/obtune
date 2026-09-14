import std.math;
import std.typecons;
import std.algorithm;
import std.array;

string f(string text, long count) 
{
    for (long i = 0; i < count; i++)
    {
        text = text.dup.reverse();
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("439m2670hlsw", 3L) == "wslh0762m934");
}
void main(){}
