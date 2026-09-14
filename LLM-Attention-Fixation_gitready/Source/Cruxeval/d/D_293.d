import std.math;
import std.typecons;
import std.algorithm;
import std.ascii;
import std.string;

string f(string text) 
{
    auto s = text.toLower();
    foreach (i; 0 .. s.length)
    {
        if (s[i] == 'x')
        {
            return "no";
        }
    }
    return all!(a => isUpper(a))(text) ? "true" : "false";
}
unittest
{
    alias candidate = f;

    assert(candidate("dEXE") == "no");
}
void main(){}
