import std.math;
import std.typecons;
string f(string s, long n, string c) 
{
    long width = cast(long)(c.length) * n;
    while (s.length < width)
    {
        s = c ~ s;
    }
    return s;
}
unittest
{
    alias candidate = f;

    assert(candidate(".", 0L, "99") == ".");
}
void main(){}
