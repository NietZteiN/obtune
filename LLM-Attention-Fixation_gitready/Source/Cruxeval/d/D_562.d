import std.math;
import std.typecons;
import std.string;

bool f(string text) 
{
    return text.toUpper == text;
}
unittest
{
    alias candidate = f;

    assert(candidate("VTBAEPJSLGAHINS") == true);
}
void main(){}
