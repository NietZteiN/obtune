import std.algorithm;
import std.array;
import std.string;

string f(string text, string value) 
{
    string ls = text;
    immutable count = ls.count(value);
    if (count % 2 == 0)
    {
        while (ls.canFind(value))
        {
            ls = ls.replace(value, "");
        }
    }
    else
    {
        ls = "";
    }
    return ls;
}

unittest
{
    alias candidate = f;

    assert(candidate("abbkebaniuwurzvr", "m") == "abbkebaniuwurzvr");
}
void main(){}
