import std.algorithm;
import std.array;
import std.string;
import std.typecons;

string f(string text, long tab_size) {
    string res = "";
    string spaces = "";
    for (int i = 0; i < tab_size - 1; ++i) {
        spaces ~= ' ';
    }
    text = text.replace("\t", spaces);
    foreach (i; 0 .. text.length) {
        if (text[i] == ' ') {
            res ~= '|';
        } else {
            res ~= text[i];
        }
    }
    return res;
}

unittest
{
    alias candidate = f;

    assert(candidate("	a", 3L) == "||a");
}
void main(){}
