import std.math;
import std.typecons;
import std.algorithm;

bool f(string text, string search) 
{
    return search.startsWith(text);
}
unittest
{
    alias candidate = f;

    assert(candidate("123", "123eenhas0") == true);
}
void main(){}
