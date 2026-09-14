import std.math;
import std.typecons;
import std.string;

string f(string text) 
{
    text = toLower(text);
    auto capitalize = text[0 .. 1].toUpper ~ text[1 .. $];
    return text[0 .. 1] ~ capitalize[1 .. $];
}
unittest
{
    alias candidate = f;

    assert(candidate("this And cPanel") == "this and cpanel");
}
void main(){}
