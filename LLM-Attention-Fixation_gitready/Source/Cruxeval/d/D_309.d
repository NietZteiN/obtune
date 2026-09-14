import std.math;
import std.typecons;
string f(string text, string suffix) 
{
    text ~= suffix;
    while (text[$-suffix.length .. $] == suffix) {
        text = text[0 .. $-1];
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("faqo osax f", "f") == "faqo osax ");
}
void main(){}
