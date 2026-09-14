import std.math;
import std.typecons;
import std.string;
import std.algorithm;

string f(string text) {
    auto a = text.strip().split(" ");
    foreach (i, word; a) {
        if (!word.isNumeric) {
            return "-";
        }
    }
    return a.join(" ");
}

unittest
{
    alias candidate = f;

    assert(candidate("d khqw whi fwi bbn 41") == "-");
}
void main(){}
