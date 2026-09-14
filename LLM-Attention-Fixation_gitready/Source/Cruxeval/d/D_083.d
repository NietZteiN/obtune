import std.math;
import std.typecons;
import std.string;
import std.conv;

string f(string text) 
{
    auto l = text.lastIndexOf('0');
    if (l == -1)
        return "-1:-1";
    return to!string(text[0 .. l].length) ~ ":" ~ to!string(text[l + 1 .. $].indexOf('0') + 1);
}
unittest
{
    alias candidate = f;

    assert(candidate("qq0tt") == "2:0");
}
void main(){}
