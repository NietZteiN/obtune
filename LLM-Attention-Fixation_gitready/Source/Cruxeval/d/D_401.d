import std.math;
import std.typecons;
string f(string text, string suffix) 
{
    if (suffix.length > 0 && text[$-suffix.length..$-1] == suffix) {
        return text[0..$-suffix.length];
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("mathematics", "example") == "mathematics");
}
void main(){}
