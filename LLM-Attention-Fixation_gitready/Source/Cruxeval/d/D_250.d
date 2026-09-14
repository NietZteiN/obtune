import std.math;
import std.typecons;
import std.string;

string f(string text) 
{
    int count = cast(int)text.length;
    for (int i = -count+1; i < 0; i++)
    {
        text ~= text[text.length + i];
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("wlace A") == "wlace Alc l  ");
}
void main(){}
