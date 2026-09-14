import std.math;
import std.typecons;
import std.algorithm;
import std.string;

string f(string s, string ch) 
{
    if(s.canFind(ch))
    {
        string sl = s.stripLeft(ch);
        if(sl.length == 0)
            sl ~= "!?";
        return sl;
    }
    return "no";
}
unittest
{
    alias candidate = f;

    assert(candidate("@@@ff", "@") == "ff");
}
void main(){}
