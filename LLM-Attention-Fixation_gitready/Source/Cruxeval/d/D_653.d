import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.array;

long f(string text, string letter) 
{
    string t = "";
    foreach (alph; text) {
        t = text.replace(alph, "");
    }
    auto result = t.split(letter);
    return result.length;
}
unittest
{
    alias candidate = f;

    assert(candidate("c, c, c ,c, c", "c") == 1L);
}
void main(){}
