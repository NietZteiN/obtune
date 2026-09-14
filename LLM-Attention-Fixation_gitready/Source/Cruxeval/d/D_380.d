import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.array;

string f(string text, string delimiter) 
{
    auto parts = text.split(delimiter);
    parts.length -= 1;
    return parts.join(delimiter);
}
unittest
{
    alias candidate = f;

    assert(candidate("xxjarczx", "x") == "xxjarcz");
}
void main(){}
