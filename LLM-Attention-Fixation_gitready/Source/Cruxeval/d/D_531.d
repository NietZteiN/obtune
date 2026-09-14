import std.math;
import std.typecons;
import std.string;

string removePrefix(string text, string prefix)
{
    if (text.startsWith(prefix))
    {
        return text[prefix.length .. $];
    }
    else
    {
        return text;
    }
}

string f(string text, string x) 
{
    if (removePrefix(text, x) == text)
    {
        return f(text[1 .. $], x);
    }
    else
    {
        return text;
    }
}

unittest
{
    alias candidate = f;

    assert(candidate("Ibaskdjgblw asdl ", "djgblw") == "djgblw asdl ");
}
void main(){}
