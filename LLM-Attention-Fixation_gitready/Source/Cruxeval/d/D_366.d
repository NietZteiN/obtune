import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string s) 
{
    auto tmp = s.toLower();
    foreach (ch; tmp)
    {
        if (tmp.canFind(ch))
        {
            tmp = tmp.replace(ch, "");
        }
    }
    return tmp;
}
unittest
{
    alias candidate = f;

    assert(candidate("[ Hello ]+ Hello, World!!_ Hi") == "");
}
void main(){}
