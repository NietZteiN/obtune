import std.math;
import std.typecons;
import std.string;
import std.algorithm;

string center(string s, long width)
{
    if (width <= s.length)
        return s;

    string result = "";
    long padding = width - s.length;
    long leftPadding = padding / 2;
    long rightPadding = padding - leftPadding;

    for (long i = 0; i < leftPadding; ++i)
        result ~= " ";

    result ~= s;

    for (long i = 0; i < rightPadding; ++i)
        result ~= " ";

    return result;
}

string f(string txt, long marker) 
{
    string[] lines = txt.split("\n");
    string[] a;
    foreach (line; lines)
    {
        string centeredLine = center(line, marker);
        a ~= centeredLine;
    }
    return a.join("\n");
}

unittest
{
    alias candidate = f;

    assert(candidate("#[)[]>[^e>
 8", -5L) == "#[)[]>[^e>
 8");
}
void main(){}
