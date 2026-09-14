import std.math;
import std.typecons;

string f(string text, long n) 
{
    if (text.length <= 2) {
        return text;
    }
    string leading_chars;
    foreach (i; 0 .. (n - text.length + 1)) {
        leading_chars ~= text[0];
    }
    return leading_chars ~ text[1 .. $-1] ~ text[$-1];
}
unittest
{
    alias candidate = f;

    assert(candidate("g", 15L) == "g");
}
void main(){}
