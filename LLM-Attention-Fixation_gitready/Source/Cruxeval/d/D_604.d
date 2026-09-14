import std.math;
import std.typecons;
import std.algorithm;

bool f(string text, string start) 
{
    return text.startsWith(start);
}
unittest
{
    alias candidate = f;

    assert(candidate("Hello world", "Hello") == true);
}
void main(){}
