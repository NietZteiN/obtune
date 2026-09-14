import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string text)
{
    text = replace(text, '"', "9");
    text = replace(text, '\'', "8");
    text = replace(text, '>', "3");
    text = replace(text, '<', "3");
    return text;
}

unittest
{
    alias candidate = f;

    assert(candidate("Transform quotations\"
not into numbers.") == "Transform quotations9
not into numbers.");
}
void main(){}
