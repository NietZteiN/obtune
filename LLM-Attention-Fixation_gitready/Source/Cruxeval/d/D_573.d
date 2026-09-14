import std.math;
import std.typecons;
import std.algorithm;
import std.string;

string f(string string, string prefix) 
{
    if (string.startsWith(prefix)) {
        return string[prefix.length..$];
    }
    return string;
}
unittest
{
    alias candidate = f;

    assert(candidate("Vipra", "via") == "Vipra");
}
void main(){}
