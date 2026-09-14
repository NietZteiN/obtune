import std.math;
import std.typecons;
string f(string text, string prefix) 
{
    return text[prefix.length..$];
}
unittest
{
    alias candidate = f;

    assert(candidate("123x John z", "z") == "23x John z");
}
void main(){}
