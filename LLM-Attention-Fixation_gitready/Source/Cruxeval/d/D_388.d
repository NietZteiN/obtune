import std.math;
import std.typecons;
import std.string;
import std.array;
import std.algorithm;

string f(string text, string characters) {
    auto characterList = characters.dup ~ " " ~ "_";

    size_t i = 0;
    while (i < text.length && canFind(characterList, text[i])) {
        i++;
    }

    return text[i .. $];
}

unittest
{
    alias candidate = f;

    assert(candidate("2nm_28in", "nm") == "2nm_28in");
}
void main(){}
