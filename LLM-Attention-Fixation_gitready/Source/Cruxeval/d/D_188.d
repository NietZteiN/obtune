import std.math;
import std.typecons;
import std.array;
import std.algorithm;
import std.string;

string[] f(string[] strings) 
{
    string[] new_strings;
    foreach (string; strings) {
        if(string.startsWith("a") || string.startsWith("p")) {
            new_strings ~= string;
        }
    }
    return new_strings;
}

unittest
{
    alias candidate = f;

    assert(candidate(["a", "b", "car", "d"]) == ["a"]);
}
void main(){}
