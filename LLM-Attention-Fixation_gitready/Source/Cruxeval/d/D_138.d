import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string text, string chars) 
{
    auto listchars = chars.dup;
    auto first = listchars[$-1];
    foreach (i; listchars[0..$-1]) {
        size_t index = text.indexOf(i);
        text = text[0..index] ~ i ~ text[index+1..$];
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("tflb omn rtt", "m") == "tflb omn rtt");
}
void main(){}
