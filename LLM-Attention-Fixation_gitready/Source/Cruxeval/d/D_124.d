import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string txt, string sep, long sep_count) 
{
    string o = "";
    while (sep_count > 0 && txt.canFind(sep) != -1)
    {
        size_t index = txt.lastIndexOf(sep);
        o ~= txt[0 .. index + sep.length];
        txt = txt[index + sep.length .. $];
        sep_count--;
    }
    return o ~ txt;
}
unittest
{
    alias candidate = f;

    assert(candidate("i like you", " ", -1L) == "i like you");
}
void main(){}
