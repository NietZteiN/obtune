import std.math;
import std.typecons;
import std.string;

string f(string text) 
{
    auto newText = text.replace(" ", "&nbsp;");
    return newText;
}

unittest
{
    alias candidate = f;

    assert(candidate("   ") == "&nbsp;&nbsp;&nbsp;");
}
void main(){}
