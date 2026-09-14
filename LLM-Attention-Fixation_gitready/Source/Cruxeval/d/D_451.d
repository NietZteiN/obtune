import std.algorithm;
import std.array;
import std.string;

string f(string text, string ch) {
    char[] textArray = text.dup;
    foreach (i, item; textArray) {
        if (item == ch[0]) {
            textArray = textArray[0 .. i] ~ textArray[i + 1 .. $];
            return textArray.idup;
        }
    }
    return text;
}

unittest
{
    alias candidate = f;

    assert(candidate("pn", "p") == "n");
}
void main(){}
