import std.algorithm;
import std.array;
import std.string;
import std.conv;

string f(string text) {
    long uppercase_index = text.indexOf('A');
    if (uppercase_index >= 0) {
        long lowercase_index = text.indexOf('a');
        if (lowercase_index >= 0) {
            return text[0 .. uppercase_index] ~ text[lowercase_index + 1 .. $];
        } else {
            return text[0 .. uppercase_index];
        }
    } else {
        auto sorted_text = text.dup.array;
        sorted_text.sort();
        return sorted_text.to!string;
    }
}

unittest
{
    alias candidate = f;

    assert(candidate("E jIkx HtDpV G") == "   DEGHIVjkptx");
}
void main(){}
