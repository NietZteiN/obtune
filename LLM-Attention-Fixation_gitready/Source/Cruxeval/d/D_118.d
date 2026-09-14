import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string text, string chars) 
{
    int num_applies = 2;
    string extra_chars = "";
    foreach(i; 0 .. num_applies) {
        extra_chars ~= chars;
        text = text.replace(extra_chars, "");
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("zbzquiuqnmfkx", "mk") == "zbzquiuqnmfkx");
}
void main(){}
