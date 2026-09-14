import std.math;
import std.typecons;
import std.string;

string f(string text, string value) 
{
    if (text.indexOf(value) == -1)
        return "";
    auto result = text.lastIndexOf(value);
    return text[0 .. result];
}
unittest
{
    alias candidate = f;

    assert(candidate("mmfbifen", "i") == "mmfb");
}
void main(){}
