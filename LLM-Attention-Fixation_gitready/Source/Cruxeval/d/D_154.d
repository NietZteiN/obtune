import std.math;
import std.typecons;
import std.algorithm;
import std.array;

string f(string s, string c) 
{
    auto words = s.split(" ").array;
    words.reverse();
    return c ~ "  " ~ words.join("  ");
}
unittest
{
    alias candidate = f;

    assert(candidate("Hello There", "*") == "*  There  Hello");
}
void main(){}
