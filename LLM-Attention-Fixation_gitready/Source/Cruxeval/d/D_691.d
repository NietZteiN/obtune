import std.math;
import std.typecons;
import std.string;

string f(string text, string suffix) 
{
    if (suffix.length > 0 && text.indexOf(suffix[$-1]) != -1) 
    {
        return f(text[0 .. $-1], suffix[0 .. $-2]);
    } 
    else 
    {
        return text;
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("rpyttc", "cyt") == "rpytt");
}
void main(){}
