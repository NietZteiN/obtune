import std.math;
import std.typecons;
bool f(string string, string c) 
{
    return string[$-c.length .. $] == c;
}
unittest
{
    alias candidate = f;

    assert(candidate("wrsch)xjmb8", "c") == false);
}
void main(){}
