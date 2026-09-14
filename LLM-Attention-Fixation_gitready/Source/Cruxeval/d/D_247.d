import std.math;
import std.typecons;
import std.ascii;

string f(string s) 
{
    foreach (char c; s)
    {
        if (!isAlpha(c))
        {
            return "no";
        }
    }

    if (s.length == 0)
    {
        return "str is empty";
    }

    return "yes";
}
unittest
{
    alias candidate = f;

    assert(candidate("Boolean") == "yes");
}
void main(){}
