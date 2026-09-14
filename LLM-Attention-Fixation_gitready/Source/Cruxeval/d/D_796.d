import std.math;
import std.typecons;
import std.algorithm;
import std.range;
import std.string;

string f(string str, string toget) 
{
    if (str.startsWith(toget)) {
        return str[toget.length .. $];
    } else {
        return str;
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("fnuiyh", "ni") == "fnuiyh");
}
void main(){}
