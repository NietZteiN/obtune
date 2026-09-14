import std.regex;
import std.algorithm;
import std.array;
import std.conv;

string f(string text) {
    if (matchFirst(text, regex(r"^[a-zA-Z_][a-zA-Z0-9_]*$"))) {
        return text.filter!(c => c >= '0' && c <= '9').array.to!string;
    } else {
        return text;
    }
}

unittest
{
    alias candidate = f;

    assert(candidate("816") == "816");
}
void main(){}
