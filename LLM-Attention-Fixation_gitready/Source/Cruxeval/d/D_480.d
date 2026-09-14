import std.math;
import std.typecons;
import std.string;
import std.conv;
import std.algorithm;
import std.array;

string f(string s, string c1, string c2) 
{
    if(s.empty)
        return s;
    auto ls = s.split(c1);
    foreach(immutable i, item; ls)
    {
        if(item.canFind(c1))
        {
            item.replaceFirst(c1, c2);
            ls[i] = item;
        }
    }
    return ls.join(c1);
}
unittest
{
    alias candidate = f;

    assert(candidate("", "mi", "siast") == "");
}
void main(){}
