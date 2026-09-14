import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string[] f(string[] names, string excluded) 
{
    foreach (i, name; names)
    {
        if (name.canFind(excluded))
        {
            name = name.replace(excluded, "");
        }
        names[i] = name;
    }
    return names;
}
unittest
{
    alias candidate = f;

    assert(candidate(["avc  a .d e"], "") == ["avc  a .d e"]);
}
void main(){}
