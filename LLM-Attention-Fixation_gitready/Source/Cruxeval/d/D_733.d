import std.math;
import std.typecons;
import std.algorithm;
import std.range;
import std.string;

string f(string text) 
{
    auto length = text.length / 2;
    auto left_half = text[0..length];
    auto right_half = text[length..$];
    right_half.retro();
    return left_half ~ right_half;
}
unittest
{
    alias candidate = f;

    assert(candidate("n") == "n");
}
void main(){}
