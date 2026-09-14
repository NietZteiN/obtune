import std.math;
import std.typecons;
import std.array;
import std.conv;
import std.algorithm;
import std.string;

string[] f(string test, string sep = " ", long maxsplit = -1) 
{
    string[] result;
    try
    {
        result = test.split(sep).reverse().array;
        if (maxsplit != -1)
            result = result[0 .. min(maxsplit, result.length)];
    }
    catch (Exception e)
    {
        result = test.split().array;
    }

    return result;
}

unittest
{
    alias candidate = f;

    assert(candidate("ab cd", "x", 2L) == ["ab cd"]);
}
void main(){}
