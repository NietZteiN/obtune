import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.conv;
import std.uni;

string f(string text) {
    if (text.length == 0) {
        return text;
    }
    if (text[0].isUpper && text[1 .. $].toLower != text[1 .. $]) {
        if (text.length > 1 && text.toLower != text) {
            return text[0].toLower.to!string ~ text[1 .. $];
        }
    } else if (text.all!(c => c.isAlpha)) {
        return text.capitalize;
    }
    return text;
}

unittest
{
    alias candidate = f;

    assert(candidate("") == "");
}
void main(){}
