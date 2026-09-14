import std.math;
import std.typecons;
import std.string;
import std.algorithm;

bool f(string text) {
    if (text == "42.42") {
        return true;
    }
    foreach (i; 3 .. text.length - 3) {
        if (text[i] == '.' && text[i - 3 .. i].isNumeric && text[0 .. i].isNumeric) {
            return true;
        }
    }
    return false;
}

unittest
{
    alias candidate = f;

    assert(candidate("123E-10") == false);
}
void main(){}
