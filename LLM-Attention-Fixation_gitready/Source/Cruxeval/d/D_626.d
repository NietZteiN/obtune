import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;
import std.conv;

string f(string line, Tuple!(string, string)[] equalityMap) {
    // Create a map from the equalityMap
    string[string] rs;
    foreach (t; equalityMap) {
        rs[t[0]] = t[1];
    }
    
    // Translate the line using the map
    string result;
    foreach (c; line) {
        if (c.to!string in rs) {
            result ~= rs[c.to!string];
        } else {
            result ~= c;
        }
    }
    return result;
}

unittest
{
    alias candidate = f;

    assert(candidate("abab", [tuple("a", "b"), tuple("b", "a")]) == "baba");
}
void main(){}
