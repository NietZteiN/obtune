import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string text, string ch) {
    size_t length = text.length;
    long index = -1;
    for (size_t i = 0; i < length; ++i) {
        if (text[i] == ch[0]) {
            index = i;
        }
    }
    if (index == -1) {
        index = length / 2;
    }
    auto new_text = text.dup;
    new_text = new_text[0 .. index] ~ new_text[index + 1 .. $];
    return cast(string)new_text;
}

unittest
{
    alias candidate = f;

    assert(candidate("o horseto", "r") == "o hoseto");
}
void main(){}
