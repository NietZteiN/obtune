import std.math;
import std.typecons;
string f(string text, string suffix) 
{
    if (text[$-suffix.length .. $] == suffix) {
        return text[0 .. $-suffix.length];
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("zejrohaj", "owc") == "zejrohaj");
}
void main(){}
