import std.math;
import std.typecons;
import std.string;

long f(string text) 
{
    return text.indexOf(",");
}
unittest
{
    alias candidate = f;

    assert(candidate("There are, no, commas, in this text") == 9L);
}
void main(){}
