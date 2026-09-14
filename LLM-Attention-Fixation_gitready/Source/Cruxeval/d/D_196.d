import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string text) 
{
    text = text.replace(" x", " x.");
    if (text.front.toUpper == text.front)
    {
        return "correct";
    }
    text = text.replace(" x.", " x");
    return "mixed";
}
unittest
{
    alias candidate = f;

    assert(candidate("398 Is A Poor Year To Sow") == "correct");
}
void main(){}
