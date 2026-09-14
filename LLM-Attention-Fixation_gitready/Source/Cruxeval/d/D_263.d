import std.math;
import std.typecons;
import std.string;
import std.array;

string[] f(string[] base, string[][] delta) 
{
    foreach (j; 0 .. delta.length)
    {
        foreach (i; 0 .. base.length)
        {
            if (base[i] == delta[j][0])
            {
                assert(delta[j][1] != base[i]);
                base[i] = delta[j][1];
            }
        }
    }
    return base;
}
unittest
{
    alias candidate = f;

    assert(candidate(["gloss", "banana", "barn", "lawn"], []) == ["gloss", "banana", "barn", "lawn"]);
}
void main(){}
