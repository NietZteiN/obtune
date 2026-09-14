import std.math;
import std.typecons;
import std.algorithm;

string f(string string, string substring) 
{
    while (string.length >= substring.length && string[0 .. substring.length] == substring) {
        string = string[substring.length .. $];
    }
    return string;
}
unittest
{
    alias candidate = f;

    assert(candidate("", "A") == "");
}
void main(){}
