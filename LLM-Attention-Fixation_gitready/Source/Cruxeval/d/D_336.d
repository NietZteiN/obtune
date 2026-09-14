import std.math;
import std.typecons;
import std.string;
import std.algorithm;

string f(string s, string sep) 
{
    s ~= sep;
    if(s.empty || sep.empty)
        return "";

    ulong startIndex = s.length;
    int count = 0;
    for(ulong i = s.length - sep.length; i < s.length; ++i)
    {
        if(s[i .. i + sep.length] == sep)
        {
            count++;
            startIndex = i;
            if(count == 2)
                break;
        }
    }

    if(startIndex == s.length)
        return s;

    return s[0 .. startIndex];
}

unittest
{
    alias candidate = f;

    assert(candidate("234dsfssdfs333324314", "s") == "234dsfssdfs333324314");
}
void main(){}
