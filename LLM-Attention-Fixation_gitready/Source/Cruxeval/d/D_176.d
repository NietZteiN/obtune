import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string text, string to_place) 
{
    size_t index = text.indexOf(to_place) + 1;
    auto after_place = text[0 .. index];
    auto before_place = text[index .. $];
    return after_place ~ before_place;
}
unittest
{
    alias candidate = f;

    assert(candidate("some text", "some") == "some text");
}
void main(){}
