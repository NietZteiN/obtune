import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string text, string to_remove) 
{
    auto new_text = text.replace(to_remove, "?");
    return new_text.replace("?", "");
}
unittest
{
    alias candidate = f;

    assert(candidate("sjbrlfqmw", "l") == "sjbrfqmw");
}
void main(){}
