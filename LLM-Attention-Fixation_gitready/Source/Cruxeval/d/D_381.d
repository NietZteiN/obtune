import std.math;
import std.typecons;
import std.conv;

string f(string text, long num_digits) 
{
    long width = num_digits > 1 ? num_digits : 1;
    string paddedText = text;
    while (paddedText.length < width)
    {
        paddedText = "0" ~ paddedText;
    }
    return paddedText;
}
unittest
{
    alias candidate = f;

    assert(candidate("19", 5L) == "00019");
}
void main(){}
