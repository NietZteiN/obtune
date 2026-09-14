import std.math;
import std.typecons;
string f(string text, long n) 
{
    auto length = text.length;
    return text[length*(n%4) .. $];
}
unittest
{
    alias candidate = f;

    assert(candidate("abc", 1L) == "");
}
void main(){}
