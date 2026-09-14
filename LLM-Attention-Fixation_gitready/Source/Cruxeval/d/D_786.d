import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string text, string letter) 
{
    auto start = text.indexOf(letter);
    if (start != -1) {
        return text[start + 1 .. $] ~ text[0 .. start + 1];
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("19kefp7", "9") == "kefp719");
}
void main(){}
