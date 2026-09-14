import std.math;
import std.typecons;
import std.string;
import std.conv;

string f(string text) {
    string t = text;
    foreach (i; t) {
        text = text.replace(i, "");
    }
    return text.length.to!string ~ t;
}

unittest
{
    alias candidate = f;

    assert(candidate("ThisIsSoAtrocious") == "0ThisIsSoAtrocious");
}
void main(){}
