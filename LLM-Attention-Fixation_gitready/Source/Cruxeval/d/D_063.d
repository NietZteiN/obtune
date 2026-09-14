import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.range;
import std.string;

string f(string text, string prefix) 
{
    while (text.startsWith(prefix)) {
        text = text[prefix.length .. $];
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("ndbtdabdahesyehu", "n") == "dbtdabdahesyehu");
}
void main(){}
