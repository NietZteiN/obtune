import std.math;
import std.typecons;
string[] f(string text) 
{
    string[] text_arr;
    foreach (j; 0 .. text.length)
    {
        text_arr ~= text[j .. $];
    }
    return text_arr;
}
unittest
{
    alias candidate = f;

    assert(candidate("123") == ["123", "23", "3"]);
}
void main(){}
