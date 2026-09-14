import std.math;
import std.typecons;
import std.array;
import std.string;

long f(string text) 
{
    return text.split("\n").length;
}
unittest
{
    alias candidate = f;

    assert(candidate("ncdsdfdaaa0a1cdscsk*XFd") == 1L);
}
void main(){}
