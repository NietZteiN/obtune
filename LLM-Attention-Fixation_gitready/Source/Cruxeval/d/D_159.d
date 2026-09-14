import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.range;

string f(string st) 
{
    string swapped = "";
    foreach (ch; st.retro)
    {
        if ('a' <= ch && ch <= 'z')
            swapped ~= (ch + 'A' - 'a');
        else if ('A' <= ch && ch <= 'Z')
            swapped ~= (ch + 'a' - 'A');
        else
            swapped ~= ch;
    }
    return swapped;
}
unittest
{
    alias candidate = f;

    assert(candidate("RTiGM") == "mgItr");
}
void main(){}
