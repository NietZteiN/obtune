import std.math;
import std.typecons;
import std.string;
import std.ascii;

string f(string text) 
{
    foreach (i, c; text)
    {
        if (!c.isDigit)
            return "no";
    }
    return "yes";
}
unittest
{
    alias candidate = f;

    assert(candidate("abc") == "no");
}
void main(){}
