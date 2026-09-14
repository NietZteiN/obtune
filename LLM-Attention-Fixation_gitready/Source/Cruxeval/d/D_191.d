import std.math;
import std.typecons;
import std.string;

bool f(string str) 
{
    return str.toUpper == str;
}
unittest
{
    alias candidate = f;

    assert(candidate("Ohno") == false);
}
void main(){}
