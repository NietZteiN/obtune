import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string text, string value) 
{
    return text.replace(value.toLower(), "");
}
unittest
{
    alias candidate = f;

    assert(candidate("coscifysu", "cos") == "cifysu");
}
void main(){}
