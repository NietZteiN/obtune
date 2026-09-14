import std.math;
import std.typecons;
import std.array;
import std.algorithm;

long f(string text, string letter) 
{
    long[char] counts;
    foreach (c; text)
    {
        counts[c] = counts.get(c, 0) + 1;
    }
    return counts.get(letter[0], 0);
}
unittest
{
    alias candidate = f;

    assert(candidate("za1fd1as8f7afasdfam97adfa", "7") == 2L);
}
void main(){}
