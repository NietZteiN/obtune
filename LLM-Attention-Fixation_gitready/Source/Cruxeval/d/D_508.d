import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.array;

string f(string text, string sep, long maxsplit) 
{
    auto splitted = text.split(sep)[0 .. text.split(sep).length / 2];
    splitted.reverse();
    splitted ~= text.split(sep)[(text.split(sep).length / 2) .. $];
    return splitted.join(sep);
}
unittest
{
    alias candidate = f;

    assert(candidate("ertubwi", "p", 5L) == "ertubwi");
}
void main(){}
