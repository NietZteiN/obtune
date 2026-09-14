import std.math;
import std.typecons;
string f(string text, string dng) 
{
    if (text.length < dng.length) {
        return text;
    }
    if (text[$-dng.length .. $] == dng) {
        return text[0 .. $-dng.length];
    }
    return text[0 .. $-1] ~ f(text[0 .. $-2], dng);
}
unittest
{
    alias candidate = f;

    assert(candidate("catNG", "NG") == "cat");
}
void main(){}
