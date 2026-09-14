import std.math;
import std.typecons;
import std.string;

string f(string text) 
{
    text = text.strip();
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("lorem ipsum") == "lorem ipsum");
}
void main(){}
