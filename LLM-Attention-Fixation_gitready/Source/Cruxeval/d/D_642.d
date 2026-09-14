import std.math;
import std.typecons;
import std.ascii;

string f(string text) 
{
    size_t i = 0;
    while (i < text.length && isWhite(text[i]))
    {
        i++;
    }
    if (i == text.length)
    {
        return "space";
    }
    return "no";
}
unittest
{
    alias candidate = f;

    assert(candidate("     ") == "space");
}
void main(){}
