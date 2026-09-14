import std.math;
import std.typecons;
string f(string text, string suffix) 
{
    if (suffix.length > 0 && text.length > 0 && text[$-suffix.length..$-1] == suffix) {
        return text[0..$-suffix.length];
    } else {
        return text;
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("spider", "ed") == "spider");
}
void main(){}
