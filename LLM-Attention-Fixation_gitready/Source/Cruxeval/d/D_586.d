import std.math;
import std.typecons;
import std.string;

long f(string text, string character) 
{
    return text.lastIndexOf(character);
}
unittest
{
    alias candidate = f;

    assert(candidate("breakfast", "e") == 2L);
}
void main(){}
