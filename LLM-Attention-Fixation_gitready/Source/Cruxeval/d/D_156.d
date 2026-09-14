import std.string;
import std.algorithm;
import std.typecons;

string f(string text, long limit, string padChar) {
    if (limit < text.length) {
        return text[0 .. limit];
    }
    return text.leftJustify(limit, padChar[0]);
}

unittest
{
    alias candidate = f;

    assert(candidate("tqzym", 5L, "c") == "tqzym");
}
void main(){}
