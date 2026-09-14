import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.array;

string f(string text, long length, long index) 
{
    auto ls = split(text);
    ls.length = min(index, ls.length);
    foreach (ref l; ls)
    {
        l = l[0 .. min(l.length, length)];
    }
    return ls.join("_");
}
unittest
{
    alias candidate = f;

    assert(candidate("hypernimovichyp", 2L, 2L) == "hy");
}
void main(){}
