import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.array;

string f(string text, string splitter) 
{
    auto words = text.toLower().split().array;
    return words.join(splitter);
}
unittest
{
    alias candidate = f;

    assert(candidate("LlTHH sAfLAPkPhtsWP", "#") == "llthh#saflapkphtswp");
}
void main(){}
