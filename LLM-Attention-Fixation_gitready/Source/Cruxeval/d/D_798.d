import std.math;
import std.typecons;
import std.algorithm;

string f(string text, string pre) 
{
    if (!text.startsWith(pre)) {
        return text;
    }
    return text[pre.length .. $];
}
unittest
{
    alias candidate = f;

    assert(candidate("@hihu@!", "@hihu") == "@!");
}
void main(){}
