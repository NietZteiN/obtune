import std.math;
import std.typecons;

string f(string text, string value)
{
    string result = text;
    while(result.length < value.length)
    {
        result ~= '?';
    }
    return result;
}

unittest
{
    alias candidate = f;

    assert(candidate("!?", "") == "!?");
}
void main(){}
