import std.math;
import std.typecons;
import std.array;
import std.string;

long f(string text) 
{
    auto strings = text.split(",");
    return - (strings[0].length + strings[1].length);
}
unittest
{
    alias candidate = f;

    assert(candidate("dog,cat") == -6L);
}
void main(){}
