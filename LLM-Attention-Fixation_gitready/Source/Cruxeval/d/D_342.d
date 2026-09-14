import std.math;
import std.typecons;
import std.algorithm;
import std.string;

bool f(string text) 
{
    return text.count("-") == text.length;
}
unittest
{
    alias candidate = f;

    assert(candidate("---123-4") == false);
}
void main(){}
